# Sanitized Demand OS set-now (commit-safe)

No `pass_token` values — safe for git. Use for local desk demo and VPS sync template.

## Local verify

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
export DEMAND_OS_MEMORY=data/demand-os/set-now-sanitized/MEMORY.json
python tools/demand_os_hub.py doctor
python tools/demand_os_hub.py status
```

Expect `data_mode: MIXED` or `REAL`, HITL queue ≥1, hunt targets from ALLOWLIST.

## VPS sync (GO deploy only)

```bash
bash tools/demand_os_sync_set_now.sh user@host:/opt/jadzia/data/demand-os/set-now
```

Set on VPS `.env`:

```bash
DEMAND_OS_SET_NOW=/opt/jadzia/data/demand-os/set-now
DEMAND_OS_MEMORY=/opt/jadzia/data/demand-os/MEMORY.json
```

## Gitleaks

Do **not** commit raw `docs/ops/demand-os/set-now/CONTENT-CALENDAR.json` with real `pass_token`. Use this pack or env-only paths on prod.
