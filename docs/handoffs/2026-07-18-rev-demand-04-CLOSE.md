# Handoff — REV-DEMAND-04 Brief HITL → sales CTA tickets

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Branch:** `master`  
**FEATURE_SHA:** `51b3ef0`  
**TIP_SHA:** `8c515e6` (docs tip; VPS SoT)  
**VPS:** `/opt/jadzia` @ `8c515e6`, `jadzia.service` **active**  
**Backup:** `/opt/jadzia/data/jadzia-pre-rev-demand-01-20260718-122719.db` (integrity ok)  
**Status:** SUCCESS — LIVE  
**Session verdict:** SUCCESS  
**Owner:** Revenue / Demand

## DONE

| Item | Result |
|------|--------|
| BLAST | `docs/handoffs/2026-07-18-rev-demand-04-BLAST.md` |
| Spawn | `spawn_brief_sales_cta_tickets` — `source=brief_sales_cta`, score≥40 |
| Queue | `sales_cta` ACTION / SLA 4h + lead disposition payload |
| UI | Commander Ack/Snooze/Close for `sales_cta` |
| Tests | `test_brief_node` + queue mapping PASS |
| Deploy | FEATURE `51b3ef0`; tip `8c515e6`; widget CTA smoke OK |
| VPS smoke | `SMOKE_OK True` — spawn + `queue_type=sales_cta` |
| Parks | Untouched; `_recover_*.py` not shipped |

## LEFT

1. Human optional: JWT disposition dogfood on LIVE Home
2. Next Demand / COI gate per `todo.json` after this CLOSE

## CRITICAL WARNINGS

- No Gate D / Mollie LIVE / min199 / live charge
- No park deletes; no ship `_recover_*.py`
- No Agent OS merge
- Health `ssh_connection=error` = known

## NEXT SESSION START

```text
STATE: REV-DEMAND-04 LIVE (brief → sales_cta)
NEXT: per todo.json active_gate after CLOSE
```
