---
status: "[CLOSE · LOCAL]"
title: "DEMAND-OS-HUB-00 — Control plane LIVE"
updated: "2026-08-01"
gate: "DEMAND-OS-HUB-00"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md §E · §F · §G · §M"
deploy_vps: false
---

# CLOSE — DEMAND-OS-HUB-00 (local)

## Decyzja Dowódcy (sesja)

STOP marketing HITL / CDP hunt. **Cel = narzędzie OS TARGET.** Marketing = PARKED_LAST.

## Evidence

| Check | Result |
|-------|--------|
| pytest demand_os (F1–F4 + Hub) | **37 passed** |
| `hub status` | OS §M screen LIVE |
| `hub money-check` | Pon slice LIVE |
| `hub a2a emit brief_icp` | JSONL bus LIVE |
| `hub memory sync` | MEMORY.json 3 layers |
| Phase0 | PASS (`parked_cash` OK) |
| VPS / Ads | untouched |

## Shipped

- `agent/demand_os/observability.py`
- `agent/demand_os/a2a_bus.py`
- `agent/demand_os/memory.py`
- `tools/demand_os_hub.py`
- `tests/test_demand_os_hub.py`
- tip: STATE · OPERATOR-TODAY · current-task · todo.json · AGENTS.md

## Tool map (OS TARGET)

| OS | Status |
|----|--------|
| L F1–F4 | LOCAL DONE |
| L F5 | parked_cash |
| E A2A runtime | LIVE (JSONL bus) |
| F Memory v0 | LIVE |
| G/M Observability | LIVE via `hub status` |
| Marketing HITL | PARKED_LAST |

## Next (tool — nie hunt)

1. Domknąć residual tool gaps jeśli są (GA4 adapter stub / growth_events→starts wire)  
2. Dopiero po Founder TOOL PASS: organic sprint HITL  
3. F5 nadal PARK do budget+GO
