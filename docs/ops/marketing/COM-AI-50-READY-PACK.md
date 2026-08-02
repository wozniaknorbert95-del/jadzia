---
status: "[ACTIVE — ready_for_human HITL]"
gate: "COM-AI-50-READY"
updated: "2026-07-31"
applies_from: "2026-08-02"
legal: "Kontrolki operacyjne — nie porada prawna. Founder + doradca NL/EU."
blast: "docs/handoffs/2026-07-31-COM-AI-50-READY-BLAST.md"
---

# COM-AI-50-READY — pack HITL (po polsku)

**Cel:** zanim pójdzie organic publish (≥**2026-08-02**) albo publiczny Concierge/widget AI — masz zatwierdzić disclosure i ewentualnie counsel.  
**Nie blokuje dziś:** shoot-plany · VHQ · Ads freeze (osobno do **2026-08-06**).

---

## HITL — Twój checklist (10–15 min)

### Krok 1 — Disclosure NL (obowiązkowe)

Proponowany tekst na widget / chat AI (dla klienta, język NL):

> Je chat met een AI-assistent van FlexGrafik. Wil je een mens? Laat het weten — we nemen over.

**Ścieżka człowieka:** klient prosi o człowieka → Ty (Telegram / WhatsApp), SPEED-TO-LEAD ręcznie.

**Twoja decyzja (wpisz poniżej / odpowiedz w czacie):**

- [x] **ACCEPT** — ten tekst NL zostaje
- [ ] **EDIT** — poprawiony tekst:

```
(tu wklej nową wersję NL)
```

### Krok 2 — Counsel przed pierwszym organic (≥2026-08-02)

- [x] **TAK** — umawiam / mam notatkę doradcy NL/EU przed publish
- [ ] **NIE** — świadomie bez counsel na start (wyższe ryzyko; nie poradą prawną)

### Krok 3 — STOP (potwierdź, że rozumiesz)

- [ ] Zero syntetycznych „twarzy klientów” jako testimonials  
- [ ] Zero fake before/after — tylko real footage  
- [ ] Ty jesteś reviewer przed każdym publish GO  
- [ ] Organic **nie wcześniej** niż 2026-08-02  
- [ ] Ads **freeze** do 2026-08-06 (osobna linia)

### Krok 4 — Odpowiedź (skopiuj do czatu / commit decision log)

```text
ACCEPT COM-AI-50
DISCLOSURE: ACCEPT | EDIT: <tekst>
COUNSEL: TAK | NIE
```

Po ACCEPT agent może dopiero planować osobny gate na wstawienie disclosure w widget UI/API (nie w tym packu).

---

## 1. Inwentarz — publiczne powierzchnie AI


| Powierzchnia         | System                                           | Klient widzi?       | Disclosure dziś                                 |
| -------------------- | ------------------------------------------------ | ------------------- | ----------------------------------------------- |
| Widget chat          | `POST /api/v1/widget/chat` → `customer_agent.py` | TAK                 | **BRAK** w UI/API — AI tylko po stronie serwera |
| Design Agent offerte | `design_agent_offerte.py`                        | TAK (jeśli exposed) | **NIESPRAWDZONE** — traktuj jako AI             |
| Commander / VHQ      | `commander-ui`                                   | NIE (operator)      | N/A (Art.50 public)                             |
| Telegram WP agent    | `telegram.py`                                    | wewnętrzne          | N/A public                                      |
| MKT 2026-W31 video   | human shoot                                      | organic później     | jeśli AI w captions/edit → disclose             |
| MKT images           | —                                                | —                   | STOP: syntetyczne mastery                       |


## 2. Proponowany disclosure (NL) — kanoniczny draft

> Je chat met een AI-assistent van FlexGrafik. Wil je een mens? Laat het weten — we nemen over.

## 3. Claims / deepfake — twarde STOP

- Bez syntetycznych twarzy „klientów” jako social proof  
- Bez fałszywych before/after  
- Publish tylko po Twoim GO

## 4. Oznakowanie / metadata (proces)


| Krok                                 | Owner             | Status            |
| ------------------------------------ | ----------------- | ----------------- |
| AI-generated vs AI-assisted vs none  | Founder + counsel | **PARKED**        |
| `ai_disclosure` na Asset Card        | Marketing ops     | szablon istnieje  |
| Machine-readable marking (KE Art.50) | Counsel           | **NIESPRAWDZONE** |


## 5. Evidence przy publish (≥2026-08-02)

- [ ] Screenshot live disclosure (pierwsza wiadomość widgetu)  
- [ ] Wersja copy + timestamp  
- [ ] Model/provider jeśli AI captions/edit (bez sekretów)  
- [ ] Imię approvera + timestamp  
- [ ] Notatka counsel (opcjonalnie)

## 6. Agent vs człowiek


| Pozycja                         | Agent                         | Ty                         |
| ------------------------------- | ----------------------------- | -------------------------- |
| Inventory + ten pack            | DONE                          | Review                     |
| Accept disclosure NL            | —                             | **WYMAGANE**               |
| Counsel przed tygodniem publish | —                             | **WYMAGANE jeśli publish** |
| Ship disclosure w widget UI/API | dopiero po ACCEPT + osobne GO | Approve                    |
| Organic publish                 | —                             | osobne GO ≥2026-08-02      |


## 7. Decision log


| Kiedy      | Kto     | Decyzja                                   |
| ---------- | ------- | ----------------------------------------- |
| 2026-07-31 | Founder | GO prep COM-AI-50 (BLAST)                 |
| *pending*  | Founder | Accept / edit disclosure                  |
| *pending*  | Founder | Counsel TAK/NIE przed organic ≥2026-08-02 |


