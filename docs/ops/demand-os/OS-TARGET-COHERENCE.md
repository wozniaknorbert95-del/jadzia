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

- **TOOL 100% SEALED** + **OPS HARDENING SEALED** (2026-08-03)
- Live P0 PARKED until [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md)
- Connectors: registry/stub fail-closed ([`CONNECTOR-BOUNDARY.md`](./CONNECTOR-BOUNDARY.md))

## Verify

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_owner_verify.py
```

## Next program

Await Dowódca unlock ceremony — agents do not push live publish.
