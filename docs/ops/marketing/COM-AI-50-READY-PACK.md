---
status: "[ACCEPTED · HITL CLOSED]"
gate: "COM-AI-50-READY"
updated: "2026-07-31"
accepted_at: "2026-07-31T14:20+02:00"
accepted_by: "Dowódca"
applies_from: "2026-08-02"
legal: "Kontrolki operacyjne — nie porada prawna. Founder + doradca NL/EU."
blast: "docs/handoffs/2026-07-31-COM-AI-50-READY-BLAST.md"
close: "docs/handoffs/2026-07-31-COM-AI-50-READY-CLOSE.md"
canonical_disclosure_nl: "Je chat met een AI-assistent van FlexGrafik. Wil je een mens? Laat het weten — we nemen over."
---

# COM-AI-50-READY — pack HITL (ACCEPTED)

**Status:** Founder **ACCEPT** 2026-07-31 · disclosure NL locked · counsel **TAK** przed organic.  
**Nie zamyka:** organic publish (osobne GO ≥2026-08-02) · ship disclosure w widget (osobny gate + GO) · Ads freeze do 2026-08-06.

---

## Decyzja Founder (zapisana)

| Pole | Wartość |
|------|---------|
| Gate | `ACCEPT COM-AI-50` |
| Disclosure | **ACCEPT** (tekst NL poniżej) |
| Counsel | **TAK** (przed pierwszym organic ≥2026-08-02) |
| Kiedy | 2026-07-31 ~14:20 +02 |

### Kanoniczny disclosure NL

> Je chat met een AI-assistent van FlexGrafik. Wil je een mens? Laat het weten — we nemen over.

**Handoff człowieka:** Telegram / WhatsApp → Dowódca (SPEED-TO-LEAD).

---

## HITL checklist (zamknięty)

- [x] ACCEPT disclosure NL  
- [x] Counsel TAK  
- [x] STOP: bez syntetycznych twarzy / fake before-after / organic &lt;2026-08-02 / Ads freeze do 2026-08-06  

---

## 1. Inwentarz — publiczne powierzchnie AI

| Powierzchnia | System | Klient widzi? | Disclosure dziś |
|--------------|--------|---------------|-----------------|
| Widget chat | `POST /api/v1/widget/chat` → `customer_agent.py` | TAK | **LIVE prod** tip `fcf6a9f` — `ai_disclosure` + first-turn prefix |
| Design Agent offerte | `design_agent_offerte.py` | TAK (jeśli exposed) | traktuj jako AI |
| Commander / VHQ | `commander-ui` | NIE | N/A |
| Telegram WP agent | `telegram.py` | wewnętrzne | N/A |
| MKT 2026-W31 video | human shoot | organic później | disclose jeśli AI captions/edit |
| MKT images | — | — | STOP: syntetyczne mastery |

## 2. Claims / deepfake — STOP

- Bez syntetycznych twarzy „klientów”  
- Bez fake before/after  
- Publish tylko po GO Foundera  

## 3. Evidence przy publish (≥2026-08-02)

- [ ] Screenshot live disclosure  
- [ ] Wersja copy + timestamp  
- [ ] Model/provider jeśli AI captions (bez sekretów)  
- [ ] Approver + timestamp  
- [ ] Notatka counsel  

## 4. Decision log

| Kiedy | Kto | Decyzja |
|-------|-----|---------|
| 2026-07-31 | Founder | GO prep COM-AI-50 (BLAST) |
| 2026-07-31 | Founder | **ACCEPT** disclosure NL (kanoniczny tekst) |
| 2026-07-31 | Founder | **Counsel TAK** przed organic ≥2026-08-02 |

## 5. Następny krok

| Gate | Co | Warunek |
|------|-----|---------|
| `COM-AI-50-SHIP` (proponowany) | Wstawienie disclosure w widget UI/API | osobne **GO** Dowódcy |
| Organic publish | MKT / Growth | ≥2026-08-02 + counsel note + osobne GO |
| Ads | paid | freeze do **2026-08-06** |
