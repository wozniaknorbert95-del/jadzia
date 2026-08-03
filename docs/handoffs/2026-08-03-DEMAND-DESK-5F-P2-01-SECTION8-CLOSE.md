---
gate: DEMAND-OS-DESK-5F-00
status: CLOSE · agent prod §8 + phone smoke proxy
updated: 2026-08-03
cache: desk-dash08
prod_tip: "5713cbc"
url: "https://api.zzpackage.flexgrafik.nl/commander/?cb=desk-dash08&_sw=1"
---

# CLOSE — 5F-P2-01 §8 prod smoke (agent)

**Verdict: PASS** — agent browser proof @ prod · viewport 375×812 mobile emulation.

Dowódca delegacja: agent przejął weryfikację §8 + phone smoke checklist.

## Phone smoke checklist

| # | Check | Result | Evidence |
|---|-------|--------|----------|
| 1 | Telegram OAuth / JWT sesja | **PASS** | „Zalogowano (sesja JWT w przeglądarce)” · JWT w storage |
| 2 | Biuro Popytu z More sheet (mobile) | **PASS** | 375px · bottom nav „Więcej” → sheet · „Biuro Popytu” navigates |
| 3 | Odśwież nie wylogowuje | **PASS** | Klik „Odśwież” → sesja JWT persists |
| 4 | Touch targets ≥44px HITL/Hunt | **PASS** | CDP: GOTOWY/BLOKADA/Dry komentarz h=44px |
| 5 | §8 design 7/7 visual | **PASS** | poniżej |

## Design §8 (`DEMAND-CONTROL-PANEL-DESIGN.md`)

| # | Acceptance | Result | Prod evidence |
|---|------------|--------|---------------|
| 1 | Robota dnia + HITL + Hunt | **PASS** | MONEY_CHECK · 3× kalendarz · 2× hunt dry |
| 2 | PARKED Desk → € nie powstaje | **PASS** | „PARKED - EUR nie powstaje…” banner |
| 3 | FIXTURE/MIXED ≠ kasa | **PASS** | „data_mode: MIXED” + żółty banner |
| 4 | Brak 5-role theater | **PASS** | „Wave1 shells: status read-only (nie 5 dzialow)” |
| 5 | Dual-cash flaga | **PASS** | „Dual-cash open_fail: 0 · [verdict, offerte_only, wizard_pushed]” |
| 6 | Brain wskazuje design doc | **PASS** | footer link „Design v2.1 · checklist §8” |
| 7 | Etap 5 build = tool 100% UI | **PASS** | P0+P1 surfaces loaded · no stuck loading |

## Verify gate

```text
pytest verify gate → 64/64 PASS
prod HTML → desk-dash08
```

## Hard DoD #12

**PASS** → unlocks **15/15** in 5F-P2-02 SEAL.
