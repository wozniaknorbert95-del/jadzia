---
status: "[BLAST · BUILD]"
title: "DEMAND-OS-HUB-00 — Control plane · Observability · A2A runtime · Memory v0"
updated: "2026-08-01"
gate: "DEMAND-OS-HUB-00"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md §E · §F · §G · §M"
founder_go: "STOP marketing HITL — finish TOOL first (Dowódca 2026-08-01)"
runtime_changes_allowed: false
deploy_vps: false
---

# BLAST — DEMAND-OS-HUB-00

## Decyzja

F1–F4 = pipeliney. **Brakuje mózgu maszyny** z OS TARGET:
- §M jeden ekran (nie markdown)
- §E A2A runtime (nie tylko tabela SLA)
- §F Memory v0 (episodic #1 hook)
- §G control plane entry (Growth Lead hub CLI)

Marketing / TT publish / FB hunt = **PARKED_LAST** do TOOL PASS.

## Scope (1-1-1)

| In | Out |
|----|-----|
| `agent/demand_os/observability.py` | Ads F5 |
| `agent/demand_os/a2a_bus.py` | Live FB/TT publish |
| `agent/demand_os/memory.py` | VPS deploy |
| `tools/demand_os_hub.py` | HQ / VHQ |
| pytest | Organic sprint HITL |

## DoD

1. `python tools/demand_os_hub.py status` → JSON: publish · comments · val FAIL · starts by utm · paid · top hook · hitl_queue
2. `money-check` → starts · paid · top hook · fail count (appendable)
3. `a2a emit brief_icp|engage_event|lead_hot` → JSONL + SLA check
4. `memory episodic` → #1 hook from ledger
5. pytest green · zero network · zero VPS
