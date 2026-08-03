---
description: Demand OS execute — TOOL+OPS SEALED · AWAIT UNLOCK. Live publish PARKED.
---

# /demand-os-execute

## Primary runner

**Use:** [`/demand-os-master-loop`](./demand-os-master-loop.md)  
**SoT:** `docs/ops/demand-os/MASTER-TODO-4.md`  
**HARD:** `.cursor/rules/demand-os-tool-first.mdc`

## Goal

Maintain Demand OS **after tool 100% SEAL**.  
Marketing live publish = **PARKED** until [`UNLOCK-LIVE-P0.md`](../../docs/ops/demand-os/UNLOCK-LIVE-P0.md).  
Test publish only if tool proof needs it (then delete).

## Hard rules

1. **No-ask** — follow MASTER-TODO-4 pointer (`4-AWAIT-UNLOCK` / post-unlock `4-P0-*` only with unlock handoff).
2. **STOP:** live TT/FB/blog without unlock · Ads · VPS bez GO · fake ledger · “Founder publish now”.
3. Seal history (5f / TOOL / OPS / UX) ≠ permission for live cadence.

## Verify (each session)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py owner-verify
```

Target: green · `live_cadence=PARKED` · no live-publish pointer drift.

## Post-unlock (only)

When `docs/handoffs/*-UNLOCK-LIVE-P0.md` exists with `UNLOCK LIVE P0`:
1. Unpark `4-P0-01` in MASTER
2. Execute HITL pack one item at a time
3. Ledger `publish=Y` only after REAL evidence
