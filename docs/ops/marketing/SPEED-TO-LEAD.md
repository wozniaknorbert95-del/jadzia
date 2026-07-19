---
status: "[ACTIVE]"
title: "Speed-to-Lead — SLA & MKT-STL-01"
process: "P-MKT-05"
updated: "2026-07-19"
---

# Speed-to-Lead (P-MKT-05)

Budżet paid umiera przy wolnym follow-upie.

## SLA (teraz — ręcznie)

| Metryka | Cel |
|---------|-----|
| Pierwszy kontakt (WhatsApp/telefon) | **&lt; 15 min** w godzinach pracy |
| Lead bez kontaktu | **&lt; 2 h** — eskalacja |
| Treść pierwszego kontaktu | Potwierdź check + link Wizard z UTM + opcjonalnie Branding Game |

Loguj medianę SLA w [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md).

## Skrypt WA (NL, skrót)

> Hoi [naam], bedankt voor je ZZP Branding Check-aanvraag. Ik stuur je binnen 1 werkdag de check. Wil je meteen starten? → Wizard-link. Liever appen: ik help je graag.

## Gate MKT-STL-01 (kod — później)

**Trigger (wszystkie):**

1. ≥ 20 leadów z Instant Form  
2. CPL w budżecie (patrz UNIT-ECONOMICS)  
3. SLA ręczne udokumentowane ≥ 1 tydzień  
4. GO Dowódcy na integrację

**Scope wtedy:** Instant Form (`leads_retrieval` / webhook) → Jadzia lead queue → HITL → Wizard (tor REV-DEMAND).  
**Nie teraz:** Messenger SDK, ManyChat prod, Ads API.

| Step | Status |
|------|--------|
| SLA process SoT | **DONE** (ten plik) |
| Ręczny follow-up przy kampanii | ready_for_human |
| Kod Instant Form → Jadzia | **PARK** do triggera |
