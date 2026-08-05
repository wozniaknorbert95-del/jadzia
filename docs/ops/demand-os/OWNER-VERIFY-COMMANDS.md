---
status: ACTIVE
updated: "2026-08-05"
pack: POST-TOOL-OWNER-VERIFY
tip: 4093179
---

# Owner Verify Commands (canonical)

**One-shot (preferred):**

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_owner_verify.py
# equivalent:
python tools/demand_os_hub.py owner-verify
```

Exit `0` = green. Includes: doctor · pointer tests · `pytest -k demand_os` · footer full · go_day summary.

**VPS:** `python` is not on PATH on prod — use the venv:
`cd /opt/jadzia && sudo -u jadzia env HOME=/home/jadzia venv/bin/python tools/demand_os_owner_verify.py`

## Full regression pack (N6 — tool seal claim)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py owner-verify
python -m pytest tests/test_demand_os_tool_first_pointer.py tests/unit/test_demand_desk_ui_contracts.py -q
python -m pytest tests -k demand_os -q
# S2: coverage gates (desk K12 + agents ≥80% line) — evidence refresh with flag:
JADZIA_EVIDENCE_WRITE=1 python -m pytest tests/unit/test_desk_coverage_k12.py tests/unit/test_agents_coverage_gate.py -q
```

Expect: exit 0 · desk cache `desk-dash13` · `active_item=4-AWAIT-UNLOCK` · no stale `2f68b64` in active pointers.

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
| doctor | `ok: true` · tip check green (STATE TOOL/OPS + live P0 PARKED) · `agents_staleness` visible — advisory local / **blocking on prod** (`DEMAND_OS_STALENESS_BLOCKING=1`, G1 2026-08-05) |
| pointer | `4-AWAIT-UNLOCK` (or `4-UNLOCK-*` / sealed tool/ops) · no stale `2f68b64` in active pointers |
| desk UI | `desk-dash13` in HTML/SW contracts |
| coverage gates | desk K12 + agents modules ≥80% line (S2) |
| worker timer | `systemctl list-timers \| grep demand-os-agents` · journal clean (C1, live 2026-08-05) |
| pytest demand_os | green |
| footer | `doctor_scope=full` · `doctor_ok` matches doctor |
| live cadence | PARKED until [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md) |

## After green

Maintain OPS · await Dowódca unlock. **Do not** open live P0.  
`go_day_ready` score ≠ Tool/OPS SEAL.

## Hub

```bash
python tools/demand_os_hub.py status --with-doctor
```
