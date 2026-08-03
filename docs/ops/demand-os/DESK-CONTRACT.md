---
status: "[SEALED · ETAP 1b DESK CONTRACT]"
updated: "2026-08-02"
gate: "DEMAND-OS-DESK-CONTRACT-00"
contract_version: "v2.1.1"
desk_design: "docs/ops/demand-os/DEMAND-CONTROL-PANEL-DESIGN.md"
golden: "tests/fixtures/desk_status_v21.min.json"
---

# Demand Desk — kontrakt API (v2.1.1)

SoT dla Etap 5 UI. Źródło: `agent.demand_os.commander_status.build_demand_os_status()`.  
CLI: `python tools/demand_os_hub.py status` (= ten sam builder).

## contract_version

`v2.1.1` — parity hub/API · A0/F · footer doctor honesty · last_real honesty · go_ready w diagnostics.

## Schema A0–F + stopka

| Strefa | JSON | Typ / uwagi |
|--------|------|-------------|
| meta | `desk` | `"Demand Desk v2.1"` |
| meta | `contract_version` | `"v2.1.1"` |
| meta | `gate` | `DEMAND-OS-DESK-CONTRACT-00` |
| meta | `marketing` | `PARKED_LAST` \| LIVE tip |
| A0 | `robota_dnia.code` | MONEY_CHECK…PARKED_STOP |
| A0 | `icp_role_week` | string |
| A0 | `iso_week` | `YYYY-Www` |
| A0 | `state` | `PARKED` \| `LIVE` |
| A | `kpi.*` | starts, wow_delta, paid, publish, val, top_hook |
| A | `kpi.validator_fail` | int **lub** `"n/a"` gdy publish=0 |
| B1 | `screen.hitl_queue[]` | `action` + `desk_action` GOTOWY\|BLOKADA\|PREP |
| B2 | `screen.hunt_queue[]` | `action` · `desk_status` READY\|SENT\|BLOCK · `draft` |
| C | (val w kpi) | |
| D | `stl.*` | open_hot, breaches, overnight, median_min |
| D | `dual_cash.open_fail` | int · kolumny verdict/offerte_only |
| E | `screen.top_wizard_assets` | max 5 · puste = `[]` + note |
| F | `week_calendar` | 5 dni Pon–Pt |
| F | `shells_line` | **1 linia** (nie 5-role grid) |
| stopka | `footer.doctor_scope` | `full` \| `lightweight` |
| stopka | `footer.doctor_ok` | **true only if scope=full and full doctor PASS** (lightweight always false) |
| stopka | `footer.doctor_files_ok` | bool — files-only slice (never shown as OK alone) |
| stopka | `footer.stale_warn` | bool |
| stopka | `data_mode` | EMPTY\|FIXTURE\|REAL\|MIXED |
| stopka | `last_real_event` | tylko REAL hits (fixture nie ustawia) |
| warn | `cash_warning` | gdy PARKED |
| diag | `diagnostics.go_ready` | CUT z top-level Desk |
| diag | `diagnostics.marketing_hitl_gate` | BLOCKED\|READY |

**Zakaz top-level:** `go_ready` (hero CUT).

## Verify

```bash
python tools/demand_os_hub.py doctor
python tools/demand_os_hub.py status
python -m pytest tests/test_demand_os_desk_contract.py tests/test_demand_os_api_desk.py -q
```

## OUT

Live publish · Ads · VPS · marketing HITL przed tool 100% UI

## UI surface

Commander `#view-demand-desk` · handoff [`DESK-UI-HANDOFF.md`](./DESK-UI-HANDOFF.md)
