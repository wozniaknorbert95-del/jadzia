---
status: "[DONE · MASTER RESIDUAL SEALED]"
title: "OS TARGET residual — etapy senior (bez marketingu)"
updated: "2026-08-01"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md"
gate: "DEMAND-OS-MASTER-RESIDUAL-00"
---

# MASTER STAGES — residual do ~100% narzędzia

Marketing / live publish / F5 / VPS = **OUT** (PARKED). Cel = domknąć wires OS §D/E/H.

| Etap | Nazwa | DoD | status |
|------|-------|-----|--------|
| **0** | Seal baseline | `hub doctor` PASS | DONE |
| **1** | jadzia.db / ops_bus → starts + leads A2A | `hub sync-db` · `hub sync-leads` | DONE |
| **2** | GA4 adapter real wrap | `mcp ga4` fail-closed · `ga4-dtl` when LIVE=1 | DONE |
| **3** | Wave1 agent shells | `tools/demand_os_agents.py` ×5 ról | DONE |
| **4** | Harden + tip | doctor + pytest + STATE tip | DONE |

## CLI

```bash
python tools/demand_os_hub.py doctor
python tools/demand_os_hub.py sync-db --dry-run
python tools/demand_os_hub.py sync-leads --dry-run
python tools/demand_os_agents.py --role validator
python tools/demand_os_mcp.py ga4
```

## Po MASTER residual

Nadal czeka Founder: `GO MARKETING HITL` (poza tym planem).
