---
status: READY_FOR_HUMAN
updated: "2026-08-03"
gate: DEMAND-OS-MARKETING-4-00
---

# Unlock live P0 — Dowódca ceremony

**env `DEMAND_OS_MARKETING_HITL=GO` ≠ cadence unlock.**  
Tool 100% SEALED + OPS hardening do not authorize live TT/FB/blog.

## Preconditions

- [ ] TOOL 100% SEAL + OPS HARDENING SEAL recorded
- [ ] `python tools/demand_os_owner_verify.py` green (local)
- [ ] VPS `hub doctor` green
- [ ] Ads remain PARK cash

## Unlock record (Founder)

```
UNLOCK LIVE P0
Date: ___________
By: Dowódca
Scope: organic HITL only (TT + FB hunt + blog) · NO Ads · NO auto-publish
```

Write handoff: `docs/handoffs/YYYY-MM-DD-UNLOCK-LIVE-P0.md`

## After unlock (human)

1. Unpark `4-P0-01` in MASTER-TODO-4 (`blocked` → `ready_for_human`)
2. TT HITL `tt_w32_install_01` via execution packet
3. Ledger `publish=Y` only after REAL video id
4. Then `4-P0-02` / `4-P0-03` separately (no bundling)

## Agent rules

- Do **not** ask Dowódca to unlock
- Do **not** treat GO env as publish permission
- Until unlock handoff exists: live P0 stays `blocked`

## STOP

Ads · boost · autonomous publish · fake ledger
