---
status: "[ACTIVE]"
title: "Marketing OS — START TUTAJ (operator)"
updated: "2026-07-19 (PROGRAM CLOSE tip 3c2fc6e ~86%)"
---

# START TUTAJ — jedna ścieżka (ADHD)

**Roadmapa:** [MKT-BRAIN-PRO.md](./MKT-BRAIN-PRO.md) — **~86%** overall · runtime **100%** · **MB_MODE=propose**  
**Handoff:** [PROGRAM-CLOSE](../../handoffs/2026-07-19-MKT-BRAIN-PRO-PROGRAM-CLOSE.md)  
**Meta:** [META-CLICK-PATH.md](./META-CLICK-PATH.md) · Scorecard: [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md)  
**Draft scorecard:** `GET …/marketing/weekly-draft` · `python scripts/mb_weekly_scorecard_draft.py`

| Co | Status |
|----|--------|
| **#1 Meta lean** | **HOLD** — €5; 7d bez edycji |
| Runtime F0→F4b | **100%** LIVE tip `3c2fc6e` |
| Weekly scorecard draft | **LIVE** (spend/CPL = wklej Ads Manager) |
| Insights agent-half | **READY** — Graph `read_insights` = HITL |
| L0 InitiateCheckout | PASS |
| L0 Purchase | ready_for_human (Mollie) |
| Agent | **observe-only** |

## Twoje 4+1 parks (HITL)

1. **H-Meta** — hold 7d → optimize ([META-CLICK-PATH](./META-CLICK-PATH.md))
2. **H-Purchase** — Mollie GO → Test Events Purchase
3. **H-Insights** — Graph `read_insights` → nowy token → `set-fb-access-token`
4. **H-WA** — Lead → WA &lt;15 min ([SPEED-TO-LEAD](./SPEED-TO-LEAD.md))
5. **H-F4x** — distribution / blog / lead webhook — dopiero po triggerach

## Operator (Telegram)

1. Karty MB w propose — scoruj / APPROVE gdy sensowne.
2. APPROVE = ticket paste-ready (nie Ads API create).
3. Co tydzień: draft scorecard w TG (bez decyzji HOLD/KILL — Ty decydujesz).

### Meta (#1 HOLD)

`zzp_branding_check_v1` · €5/dzień · camp `120254517992840360`.

**Zakaz:** Ads API create · Mollie LIVE · fake PASS · reorder STATUS BOARD bez GO.
