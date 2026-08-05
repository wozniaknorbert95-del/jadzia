---
status: "[CLOSE · LOCAL]"
title: "DEMAND-F3-00 — TT/FB connectors"
updated: "2026-08-01"
gate: "DEMAND-OS-F3-00"
deploy_vps: false
---

# CLOSE — DEMAND-F3-00 (local)

## Decision

Connectors = **allowlist gate + anti-spam + engage API**, nie masowy Graph spam.  
Live comment = PARK (wymaga `DEMAND_OS_LIVE_COMMENT=1` + przyszłe GO). Smoke = mock transport (DoD bez sekretów).

## Evidence

| Check | Result |
|-------|--------|
| pytest F1+F2+F3 | **26 passed** |
| `demand_os_f3.py smoke` | **SMOKE PASS** (1 read + 1 comment) |
| pending_fill | DENY |
| same copy → 2 groups | AntiSpamError |
| F2 R1 fix | unique URLs (caption+utm same link OK) |

## Shipped

- `ALLOWLIST.json` (max 5 groups · own FB/TT active)
- `agent/demand_os/connectors/*`
- `tools/demand_os_f3.py`
- `tests/test_demand_os_f3_connectors.py`

## Next

`GO BUILD demand-f4` (Blog ICP pipeline) **lub** human fill FB groups 1–5.
