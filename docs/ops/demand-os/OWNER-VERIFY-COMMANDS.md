---
status: ACTIVE
updated: "2026-08-03"
pack: TOOL-100-OWNER-VERIFY
---

# Owner Verify Commands (canonical)

**One-shot (preferred):**

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_owner_verify.py
```

Exit `0` = green. Includes: doctor · pointer tests · `pytest -k demand_os` · footer full · go_day summary.

## Manual pack (equivalent)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest tests/test_demand_os_tool_first_pointer.py -q
python -m pytest tests -k demand_os -q
python -c "from agent.demand_os.commander_status import build_demand_os_status; import json; print(json.dumps(build_demand_os_status(with_full_doctor=True)['footer'], indent=2))"
```

## Expected

| Check | Pass |
|-------|------|
| doctor | `ok: true` · tip `TOOL_FIRST/PARKED` |
| pointer | `4-TOOL-*` or `4-OPS-*` · no stale `2f68b64` in active pointers |
| pytest demand_os | green |
| footer | `doctor_scope=full` · `doctor_ok` matches doctor |
| live cadence | PARKED until [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md) |

## After green

Maintain OPS · await Dowódca unlock. **Do not** open live P0.

## Hub

```bash
python tools/demand_os_hub.py status --with-doctor
```
