---
status: "[PASS · TOOL 100% SEALED · score ≠ seal]"
updated: "2026-08-03"
sot: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md"
phases: "docs/ops/demand-os/PROGRAM-PHASES.md"
scope: "TOOL/MACHINE coherence — NOT live marketing"
---

# OS TARGET — spójność narzędzia

## Truth table

| Pojęcie | Znaczenie | Jak mierzyć |
|---------|-----------|-------------|
| **Artifact score** (`go_day_ready`) | Checklist tool-side readiness | `week_ritual.go_day_ready()` score |
| **Integrity doctor** | SoT + modules + desk contract green | `hub doctor` → `ok: true` |
| **Tool 100% SEAL** | Formal close residual program | handoff `DEMAND-OS-TOOL-100-SEAL-CLOSE` |
| **Live cadence** | TT/FB/blog publish rhythm | PARKED until Dowódca unlock |

**Nie mylić:** `go_day_ready score=100` ≠ Tool 100% SEAL ≠ permission for live publish.

## Etap 1 — zamknięte (historical wires)

RBAC · §M UI · GDrive honesty · blog→pipeline · MCP calendar/gate/ga4-utm · fatigue · R9 · design_agent UTM · hub CLI RBAC · doctor coherence checks · PROGRAM-PHASES tip.

## Current

- **TOOL 100% SEALED** (2026-08-03) · live P0 PARKED
- Doctor + pytest demand_os green under TOOL FIRST SoT
- Connectors: registry/stub fail-closed (see [`CONNECTOR-BOUNDARY.md`](./CONNECTOR-BOUNDARY.md))

## Verify

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest tests -k demand_os -q
python -m pytest tests/test_demand_os_tool_first_pointer.py -q
```

## Next program

Finish `4-TOOL-01` residual → Tool 100% SEAL → **then** Dowódca may unlock live P0 (separate ceremony).
