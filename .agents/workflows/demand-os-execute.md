---
description: Demand OS execute — TOOL FIRST (Etap 4). Live publish PARKED.
---

# /demand-os-execute

## Primary runner

**Use:** [`/demand-os-master-loop`](./demand-os-master-loop.md)  
**SoT:** `docs/ops/demand-os/MASTER-TODO-4.md`  
**HARD:** `.cursor/rules/demand-os-tool-first.mdc`

## Goal

Maintain / finish Demand OS **tool 100%**.  
Marketing live publish = **PARKED**. Test publish only if tool proof needs it (then delete).

## Hard rules

1. **No-ask** — follow MASTER-TODO-4 pointer (`4-TOOL-*`).
2. **STOP:** live TT/FB/blog · Ads · VPS bez GO · fake ledger · “Founder publish now”.
3. Seal history (5f / integrity) ≠ permission for live cadence.

## Verify (each session)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest tests -k demand_os -q
```

Target: green · no live-publish pointer drift.
