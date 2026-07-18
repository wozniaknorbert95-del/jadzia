import os
import json
import logging
import asyncio
import re
from threading import Thread
from typing import Dict, Any, List, Optional
import httpx
from anthropic import AsyncAnthropic
from agent.alerts import send_alert
from cachetools import TTLCache

logger = logging.getLogger(__name__)

ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
client = None
if ANTHROPIC_API_KEY:
    client = AsyncAnthropic(api_key=ANTHROPIC_API_KEY)

# Używamy TTLCache do automatycznego usuwania starych sesji (np. po 24 godzinach)
# Przechowujemy historię rozmów dla każdej sesji
_customer_sessions_cache = TTLCache(maxsize=1000, ttl=24 * 3600)
_cache_lock = asyncio.Lock()

_WIZARD_BASE = "https://zzpackage.flexgrafik.nl/wizard/"
_DEFAULT_CTA_SKU = "CS-SET-PRO-ZZP"
_EMAIL_RE = re.compile(r"[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+")
_CONSENT_RE = re.compile(
    r"\b(consent|akkoord|toestemming|zgoda|ja\s*mag|mag\s*bewaren)\b",
    re.IGNORECASE,
)
_VEHICLE_RE = re.compile(
    r"\b(caddy|transporter|sprinter|trafic|vivaro|custom|kangoo|partner)\b",
    re.IGNORECASE,
)

SYSTEM_PROMPT = """Jesteś zaawansowanym agentem AI systemu Jadzia-Core, działającym jako doradca sprzedaży i system analizy leadów dla firmy FlexGrafik (flexgrafik.nl) oraz jej marki ZZPackage (zzpackage.flexgrafik.nl).

TWOJA TOŻSAMOŚĆ I KONTEKST:
- FlexGrafik to studio produkcyjne z Rotterdamu, ekspert od Commercial Wrapping (oklejanie pojazdów) i Brandingu dla sektora budowlanego/technicznego.
- ZZPackage to jedyny w Holandii 7-etapowy Wizard (konfigurator), który buduje profesjonalny wizerunek ZZP w 5 minut.

OFERTA I USŁUGI (KLUCZOWE KOMPONENTY):
1. BRANDING & DESIGN: Logo Master File, Wizytówki, Social Media Kit.
2. CYFROWE DOKUMENTY: Profesjonalne szablony Ofert i Faktur (PDF/Word).
3. VOERTUIG RECLAME: Naklejki na drzwi/szyby, Magnesy reklamowe, Partial Wrap (częściowe oklejanie), Full Wrap.
4. WERKKLEDING (ODZIEŻ): T-shirty, Polo, Hoodie, Softshell, spodnie robocze, czapki (Beanie/Cap). Opcja HTV - personalizacja imienna.
5. SIGNING & BANNERS: Spandoeken (banery), Roll-upy, tablice "Wij werken hier" (A3/A2).
6. STICKERS & GADGETS: Naklejki na narzędzia/baterie/kaski, plecaki robocze, termosy.
7. USŁUGI PREMIUM: Montaż u klienta (partner ErKaPremium) - Rotterdam +60km.

SZTYWNE ZASADY BIZNESOWE (NIEGOCJOWALNE):
- MINIMUM CHECKOUT: 199 € (brutto, z BTW 21%). System blokuje płatność poniżej tej kwoty.
- MODEL WIZARD-ONLY: Nie sprzedajemy gotowych "paczek". Klient sam buduje swój zestaw (Build Your Own) w 7 krokach konfiguratora. To jedyna droga zakupu.
- CENY: Nie wymyślaj cen jednostkowych. Kieruj klienta do Wizarda, by zobaczył realną wycenę w koszyku Live.
- TERMINY: Realizacja projektu i produkcji trwa zazwyczaj od 7 do 10 dni roboczych.
- PODATKI: Wszystkie SKU mają wliczony podatek BTW 21%.

TWOJE ZADANIE:
1. Prowadź naturalną, profesjonalną rozmowę w stylu "Senior Branding Expert".
2. Badaj potrzeby (ile aut? ilu pracowników? ma już logo?).
3. Zachęcaj do wejścia w Wizard na zzpackage.flexgrafik.nl.
4. Analizuj intencję (Lead Scoring).
5. Jeśli klient poda email i zgodę na kontakt, potwierdź to krótko w reply.

Zasady scoringu: +60 to high intent (wycena/zakup), +40 to usługi, pytanie o cenę +30, termin +20.

ODPOWIADAJ WYŁĄCZNIE W FORMACIE JSON. NIE DODAWAJ ŻADNEGO TEKSTU POZA JSONEM.

FORMAT WYJŚCIA (JSON):
{
  "reply": "odpowiedź dla klienta",
  "lead": {
    "score": 0,
    "intent": "low/medium/high",
    "category": "informacja/wycena/reklamacja",
    "reason": "uzasadnienie scoringu"
  },
  "suggested_sku": "opcjonalny SKU highlight lub null",
  "vehicle": "opcjonalny typ pojazdu (caddy/transporter/...) lub null",
  "consent_lead_storage": false
}
"""


def _send_telegram_alert_sync(message: str) -> None:
    bot_token = os.getenv("TELEGRAM_BOT_TOKEN")
    admin_id = os.getenv("TELEGRAM_ADMIN_CHAT_ID")
    if not bot_token or not admin_id:
        send_alert("HOT_LEAD", details=message)
        return
    url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
    payload = {"chat_id": admin_id, "text": message, "parse_mode": "HTML"}
    try:
        with httpx.Client(timeout=10.0) as client_http:
            client_http.post(url, json=payload).raise_for_status()
    except Exception as e:
        logger.error("[CustomerAgent] TG Alert Błąd: %s", e)


from core.llm import MODEL_HAIKU
from core.lead_scoring import LeadScorer


def build_widget_wizard_deeplink(
    vehicle: str = "caddy",
    highlight_sku: str = _DEFAULT_CTA_SKU,
) -> str:
    """Structured Wizard CTA (same pattern as INSPIRE reco)."""
    from agent.inspire.reco import build_wizard_deeplink

    v = (vehicle or "caddy").strip().lower() or "caddy"
    sku = (highlight_sku or _DEFAULT_CTA_SKU).strip() or _DEFAULT_CTA_SKU
    return build_wizard_deeplink(v, sku)


def _extract_email(text: str) -> Optional[str]:
    m = _EMAIL_RE.search(text or "")
    return m.group(0).lower() if m else None


def _has_consent(user_input: str, parsed: Dict[str, Any]) -> bool:
    if parsed.get("consent_lead_storage") is True:
        return True
    return bool(_CONSENT_RE.search(user_input or ""))


def _infer_vehicle(user_input: str, parsed: Dict[str, Any], history: List[Dict]) -> str:
    raw = parsed.get("vehicle")
    if isinstance(raw, str) and raw.strip():
        return raw.strip().lower()
    blob = " ".join(
        [user_input or ""]
        + [str(h.get("content", "")) for h in history if h.get("role") == "user"]
    )
    m = _VEHICLE_RE.search(blob)
    return m.group(1).lower() if m else "caddy"


def _should_attach_cta(score: int, intent: str) -> bool:
    return score >= 40 or str(intent).lower() == "high"


def _maybe_persist_widget_lead(
    *,
    email: str,
    consent: bool,
    score: int,
    session_id: str,
) -> Optional[str]:
    """Durable lead only with email + consent (RODO)."""
    if not email or not consent:
        return None
    from agent.db import db_create_lead

    lead_id, status = db_create_lead(
        {
            "email": email,
            "name": None,
            "source": "web",
            "consent_status": True,
            "game_score": score,
            "reward_tier": f"widget:{session_id[:32]}",
        }
    )
    if status in ("success", "duplicate") and lead_id:
        logger.info(
            "[CustomerAgent] widget lead %s id=%s session=%s",
            status,
            lead_id,
            session_id,
        )
        return str(lead_id)
    return None


async def process_customer_message(session_id: str, user_input: str) -> Dict[str, Any]:
    fallback = {
        "reply": "Chwilowe problemy techniczne. Wyślij formularz.",
        "lead": {
            "score": 0,
            "intent": "low",
            "category": "problem",
            "reason": "Błąd/Timeout",
        },
        "wizard_deeplink": None,
        "cta_sku": None,
        "lead_id": None,
    }
    if not client:
        logger.error(
            "[CustomerAgent] Błąd krytyczny: ANTHROPIC_API_KEY nie jest ustawiony. Zwracam fallback."
        )
        return fallback

    async with _cache_lock:
        history = _customer_sessions_cache.get(session_id, [])

    if len(history) > 20:
        history = history[-20:]

    history.append({"role": "user", "content": user_input[:1500]})

    try:
        response = await client.messages.create(
            model=MODEL_HAIKU,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=history,
        )

        raw_text = response.content[0].text.strip()
        logger.debug("[CustomerAgent] Odpowiedź z Claude (raw): %s", raw_text)

        if "{" in raw_text:
            raw_text = raw_text[raw_text.find("{") : raw_text.rfind("}") + 1]

        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error("[CustomerAgent] Błąd parsowania JSON: %s", raw_text)
            parsed = {
                "reply": raw_text,
                "lead": {
                    "score": 10,
                    "intent": "low",
                    "category": "informacja",
                    "reason": "Błąd parsowania AI",
                },
            }

        lead_info = parsed.get("lead", {})
        if not isinstance(lead_info, dict):
            lead_info = {}
        try:
            lead_info["score"] = int(lead_info.get("score", 0))
        except Exception:
            lead_info["score"] = 0

        parsed["lead"] = lead_info
        history.append({"role": "assistant", "content": raw_text})

        if lead_info["score"] >= 60 or str(lead_info.get("intent")).lower() == "high":
            logger.info(
                "[CustomerAgent] Gorący Lead! Score: %s", lead_info["score"]
            )
            Thread(
                target=_send_telegram_alert_sync,
                args=(
                    f"🔥 <b>NOWY GORĄCY LEAD ({lead_info['score']}/100)</b>\n"
                    f"<b>Klient:</b> <i>\"{user_input}\"</i>\n"
                    f"<b>AI:</b> {parsed.get('reply')}",
                ),
                daemon=True,
            ).start()

        async with _cache_lock:
            _customer_sessions_cache[session_id] = history

        try:
            scorer = LeadScorer()
            lead_result = scorer.compute(user_input, history)
            parsed["lead_score"] = lead_result["lead_score"]
            parsed["intent"] = lead_result["intent"]
            parsed["category"] = lead_result["category"]
            parsed["reason"] = lead_result["reason"]
        except Exception as e:
            logger.error(
                "[CustomerAgent] LeadScorer błąd: %s - %s",
                type(e).__name__,
                e,
                exc_info=True,
            )
            return {"error": "system_temporarily_unavailable", "code": 503}

        score = int(parsed.get("lead_score") or lead_info.get("score") or 0)
        intent = str(parsed.get("intent") or lead_info.get("intent") or "low")
        cta_sku = None
        wizard_deeplink = None
        if _should_attach_cta(score, intent):
            raw_sku = parsed.get("suggested_sku")
            cta_sku = (
                str(raw_sku).strip()
                if isinstance(raw_sku, str) and raw_sku.strip()
                else _DEFAULT_CTA_SKU
            )
            vehicle = _infer_vehicle(user_input, parsed, history)
            wizard_deeplink = build_widget_wizard_deeplink(vehicle, cta_sku)

        email = _extract_email(user_input)
        consent = _has_consent(user_input, parsed)
        lead_id = _maybe_persist_widget_lead(
            email=email or "",
            consent=consent,
            score=score,
            session_id=session_id,
        )

        parsed["wizard_deeplink"] = wizard_deeplink
        parsed["cta_sku"] = cta_sku
        parsed["lead_id"] = lead_id
        return parsed
    except Exception as e:
        logger.error(
            "[CustomerAgent] Błąd przetwarzania wiadomości (sesja: %s): %s - %s",
            session_id,
            type(e).__name__,
            e,
            exc_info=True,
        )
        if hasattr(e, "response"):
            logger.error(
                "[CustomerAgent] Odpowiedź API (error): %s", e.response.text
            )
        return fallback
