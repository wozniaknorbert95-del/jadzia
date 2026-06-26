import os
import json
import logging
import asyncio
from threading import Thread
from typing import Dict, Any, List
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
  }
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
        logger.error(f"[CustomerAgent] TG Alert Błąd: {e}")

from core.llm import MODEL_HAIKU
from core.lead_scoring import LeadScorer

async def process_customer_message(session_id: str, user_input: str) -> Dict[str, Any]:
    fallback = {"reply": "Chwilowe problemy techniczne. Wyślij formularz.", "lead": {"score":0, "intent":"low", "category":"problem", "reason":"Błąd/Timeout"}}
    if not client:
        logger.error("[CustomerAgent] Błąd krytyczny: ANTHROPIC_API_KEY nie jest ustawiony. Zwracam fallback.")
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
            messages=history
        )
        
        raw_text = response.content[0].text.strip()
        logger.debug(f"[CustomerAgent] Odpowiedź z Claude (raw): {raw_text}")
        
        if "{" in raw_text:
            raw_text = raw_text[raw_text.find("{"):raw_text.rfind("}")+1]
            
        try:
            parsed = json.loads(raw_text)
        except json.JSONDecodeError:
            logger.error(f"[CustomerAgent] Błąd parsowania JSON: {raw_text}")
            parsed = {"reply": raw_text, "lead": {"score": 10, "intent": "low", "category": "informacja", "reason": "Błąd parsowania AI"}}

        lead_info = parsed.get("lead", {})
        if not isinstance(lead_info, dict): lead_info = {}
        try: lead_info["score"] = int(lead_info.get("score", 0))
        except: lead_info["score"] = 0
            
        parsed["lead"] = lead_info
        history.append({"role": "assistant", "content": raw_text})
        
        if lead_info["score"] >= 60 or str(lead_info.get("intent")).lower() == "high":
            logger.info(f"[CustomerAgent] Gorący Lead! Score: {lead_info['score']}")
            Thread(target=_send_telegram_alert_sync, args=(f"🔥 <b>NOWY GORĄCY LEAD ({lead_info['score']}/100)</b>\n<b>Klient:</b> <i>\"{user_input}\"</i>\n<b>AI:</b> {parsed.get('reply')}",), daemon=True).start()
        
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
            logger.error(f"[CustomerAgent] LeadScorer błąd: {type(e).__name__} - {e}", exc_info=True)
            return {"error": "system_temporarily_unavailable", "code": 503}

        return parsed
    except Exception as e:
        logger.error(f"[CustomerAgent] Błąd przetwarzania wiadomości (sesja: {session_id}): {type(e).__name__} - {e}", exc_info=True)
        if hasattr(e, 'response'):
            logger.error(f"[CustomerAgent] Odpowiedź API (error): {e.response.text}")
        return fallback
