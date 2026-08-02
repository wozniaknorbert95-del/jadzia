---
status: "[CLOSE · LOCAL]"
title: "DEMAND-F1-00 — UTM Lock + growth_events"
updated: "2026-08-01"
gate: "DEMAND-OS-F1-00"
deploy_vps: false
---

# CLOSE — DEMAND-F1-00 (local)

## Done

1. TikTok test post **DELETED** (Studio → Delete → confirm · “Post deleted”).
2. Publish **FROZEN** (OPERATOR · STATE · W1-03 blocked · GO-DAY frozen).
3. `GO BUILD demand-f1` recorded (Dowódca: usuń + wdrażaj narzędzie).
4. Shipped:
   - `agent/demand_os/utm_lock.py`
   - `agent/demand_os/growth_events.py`
   - `tools/demand_os_utm.py`
   - `tests/test_demand_os_utm_lock.py` — **8 passed**
   - ledger audit — **3/3 PASS**
   - `GROWTH-EVENTS.jsonl` — bridge_proof + publish_frozen

## STOP retained

VPS deploy · Ads · organic publish · HQ polish

## Next

`GO BUILD demand-f2` (Validator + calendar MCP) **albo** wire UTM Lock do DA/Widget — decyzja: **F2** (Validator egzekwuje lock przed publish).
