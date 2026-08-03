---
status: ACTIVE
updated: "2026-08-03"
pack: TOOL-100-OWNER-VERIFY
---

# Owner Verify Commands (canonical)

**Run at the start of every Demand OS session.**  
Full doctor only — never treat lightweight footer as PASS.

## One pack

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest tests/test_demand_os_tool_first_pointer.py -q
python -m pytest tests -k demand_os -q
python -c "from agent.demand_os.week_ritual import go_day_ready; import json; print(json.dumps({k: go_day_ready().get(k) for k in ('score','ok','marketing','marketing_hitl_gate')}, indent=2))"
python -c "from agent.demand_os.commander_status import build_demand_os_status; import json; f=build_demand_os_status(with_full_doctor=True)['footer']; print(json.dumps({k:f.get(k) for k in ('doctor_ok','doctor_scope','doctor_files_ok')}, indent=2))"
```

## Expected (TOOL FIRST)

| Check | Pass |
|-------|------|
| doctor | `ok: true`, tip detail `TOOL_FIRST/PARKED` (or coherent historical pair) |
| pointer test | green · `active_item` = `4-TOOL-*` |
| pytest demand_os | green |
| go_day | `score` reported (artifact; ≠ seal) |
| footer (full) | `doctor_scope=full` · `doctor_ok` matches doctor |

## Fail cases

| Symptom | Meaning |
|---------|---------|
| doctor tip STATE mismatch | SoT drifted from TOOL FIRST contract |
| `doctor_ok=true` with `doctor_scope=lightweight` | **BUG** — false green |
| `active_item` = `4-P0-*` | pointer drift — STOP, re-sync MASTER |
| RECOMMENDED_NEXT = Founder publish | stale handoff — ignore |

## Hub status

```bash
python tools/demand_os_hub.py status --with-doctor
```

`--with-doctor` required for footer full PASS. Default status uses lightweight scope (`doctor_ok=false` by design).

## After green

Continue **tool residual** (`4-TOOL-01`).  
Do **not** open live P0 / Founder publish.  
Test publish only via [`4-TOOL-02-TEST-PUBLISH.md`](./4-TOOL-02-TEST-PUBLISH.md) if tool proof needs it.
