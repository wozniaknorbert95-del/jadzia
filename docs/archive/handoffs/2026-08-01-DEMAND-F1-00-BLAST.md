---
status: "[BLAST · CLOSED LOCAL]"
title: "DEMAND-F1-00 — UTM Lock + growth_events"
updated: "2026-08-01"
gate: "DEMAND-OS-F1-00"
todo: DOS-F1-GO · DOS-F1-01
founder_go: "GO BUILD demand-f1 (Dowódca 2026-08-01 — delete test TT + kontynuuj wdrożenie)"
runtime_changes_allowed: false
deploy_vps: false
---

# BLAST — DEMAND-F1-00

## Intent (1-1-1)

Zbudować **UTM Lock + growth_events** w `jadzia-core` (lokalnie).  
Publish organic **FROZEN**. Zero Ads · zero HQ · zero VPS.

## Binary DoD

| # | DoD | Pass when |
|---|-----|-----------|
| D1 | UTM builder | `build_wizard_utm(channel, role, asset_id)` = template C.1 #3 |
| D2 | UTM validator | reject bare Wizard / missing params / wrong host / multi-CTA |
| D3 | growth_events | append-only event log: `cta_issued` · `cta_validated` · `cta_rejected` |
| D4 | CLI | `python tools/demand_os_utm.py build|validate|audit-ledger` |
| D5 | Tests | pytest green for lock + events |
| D6 | Ledger audit | sample LEDGER rows → 100% UTM PASS (or FAIL listed) |

## Work packages

1. **WP-A** `agent/demand_os/utm_lock.py` + `growth_events.py`
2. **WP-B** `tools/demand_os_utm.py` CLI
3. **WP-C** `tests/test_demand_os_utm_lock.py`
4. **WP-D** SoT tip: STATE · TODO · OPERATOR · todo.json

## STOP

Publish TT/FB · Ads · Mollie · VPS deploy · dashboard polish · merge OS↔jadzia
