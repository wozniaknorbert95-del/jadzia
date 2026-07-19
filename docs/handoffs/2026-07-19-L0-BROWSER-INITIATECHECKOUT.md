---
date: 2026-07-19
gate: MKT-INSTR-01 / L0
status: CLOSE (partial — InitiateCheckout PASS)
---

# Handoff — L0 browser: InitiateCheckout PASS

## Verdict

**PASS** — Meta Test Events otrzymał `InitiateCheckout` (UI PL: *Zainicjowanie przejścia do kasy*) z Wizard `zzpackage.flexgrafik.nl`.

## Evidence

- Pixel: `1084197063740065` (Piksel konta Norbert Woźniak)
- act: `758460034566524`
- test_event_code: `TEST39712`
- Timestamp: **2026-07-19 15:24:32** · Przeglądarka · Ręczna konfiguracja · Przetworzono
- Cart: €218 excl. (F-001 + DF-006), min. €199

## PARK

- **Purchase** — sesja zatrzymana na `/afrekenen/`; brak GO na live Mollie.
- CAPI / Purchase match quality — osobny ticket.

## SoT updated

- `docs/ops/marketing/L0-INSTRUMENTATION.md`
