# Handoff — REV-DEMAND-01a DOGFOOD (no pay)

**Date:** 2026-07-18  
**Status:** PASS (local / code-path)  
**Active gate after:** `REV-DEMAND-01b` shipped in same session

## Scenarios

| # | Scenario | Result | Evidence |
|---|----------|--------|----------|
| 1 | INSPIRE deeplink builder | PASS | `build_wizard_deeplink` reused by widget CTA tests |
| 2 | Widget CTA path | PASS | `tests/unit/test_widget_demand_cta.py` — deeplink + optional lead |
| 3 | Lead persist + hot queue | PASS | lead create + disposition hide from queue |
| 4 | Commander disposition | PASS | `tests/unit/test_lead_disposition.py` |
| 5 | VPS live HTTP dogfood | DEFERRED | Manual: after Dowódca deploy `master`; use `docs/ops/JADZIA-REVENUE-DOGFOOD.md` |

## STOP honored

No Mollie, no real order, no Gate D, no min199 change.

## Parks (still present)

REV-R0-02C, S1-01, OPS-FB-HYGIENE-01, B3-*, C1-01, D1-03

## NEXT

Deploy checklist for Dowódca (manual). Playbook F4 for click-test on VPS.
