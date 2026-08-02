---
status: "[ACTIVE · SOT]"
title: "Demand OS — Calendar SoT split"
updated: "2026-08-01"
os_target: "E content_calendar"
---

# Calendar SoT

| Calendar | Path / store | Purpose |
|----------|--------------|---------|
| **Growth gate (Demand OS)** | `docs/ops/demand-os/set-now/CONTENT-CALENDAR.json` via `agent/demand_os/content_calendar.py` | F2 validate · pass_token · `hub` / `f2 gate` · publish DENY/ALLOW |
| **Ops calendar (legacy)** | SQLite INT-010 · `agent/nodes/content_calendar_node.py` | COI ops scheduling — **not** growth publish SoT |

## Rules

1. Growth publish / Demand OS path reads **only** `CONTENT-CALENDAR.json`.
2. Ops SQLite must **not** be treated as Val/pass_token source.
3. Publisher with `asset_id` → Demand OS gate (`publish_gate_bridge`).
4. Legacy ops rows without `asset_id` may use `skip_demand_gate=True`.
