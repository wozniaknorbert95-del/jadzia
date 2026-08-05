---
gate: DEMAND-OS-DESK-5B-00
status: CLOSE · AGENT COMPLETE · SEAL PENDING Dowódca §8 prod
updated: 2026-08-02
supersedes: 2026-08-02-DEMAND-DESK-GAP-CLOSE-CLOSE.md (fałszywy 15/15)
spec: docs/superpowers/specs/2026-08-02-demand-desk-hardening-design.md
---

# CLOSE — Etap 5b Biuro Popytu Dashboard Hardening (agent)

## Werdykt

**Agent work COMPLETE.** Tool UI hardened lokalnie · **75 desk-related pytest PASS**.  
**Nie SEALED** — Hard DoD **14/15** do czasu Dowódca §8 prod + deploy GO.

Marketing = **PARKED_LAST** (bez zmian).

## Hard DoD 15/15 — stan końcowy

| # | Punkt | Status | Dowód |
|---|-------|--------|-------|
| 1 | HTML A0–F + stopka | **PASS** | `test_demand_desk_ui_contracts.py` |
| 2 | Render 1:1 status API | **PASS** | `test_render_desk_golden.py` + hub contract |
| 3 | FIXTURE/PARKED/n/a val | **PASS** | golden MIXED fixture + banner tests |
| 4 | HITL bez publish | **PASS** | `test_hitl_decision_persists.py` |
| 5 | Hunt dry + reload SENT | **PASS** | `test_hunt_dry_updates_queue.py` · fix `hunt_dry.py` log_path |
| 6 | ICP + ledger RBAC | **PASS** | `test_demand_desk_api_extended.py` viewer 403 |
| 7 | VHQ CTA + KPI | **PASS** | `test_vhq_firm_ia_contracts.py` |
| 8 | Deep link `?view=` | **PASS** | `test_demand_desk_flow.py` |
| 9 | brak go_ready hero | **PASS** | API + static tests |
| 10 | Static tests + nav 5 | **PASS** | `desk-dash03` w HTML/sw/tests |
| 11 | doctor + pytest demand_os | **PASS** | 75 desk suite @ sanitized set-now |
| 12 | **Manual §8 Dowódca** | **PENDING** | prod visual + design §8 checkboxy |
| 13 | DESK-UI-HANDOFF.md | **PASS** | Known gaps → agent closed |
| 14 | CLOSE + evidence | **PASS** | ten plik |
| 15 | marketing PARKED_LAST | **PASS** | SoT sweep · brak „next=marketing” |

## Deliverables S0–S7 (agent)

| Sesja | Done |
|-------|------|
| S0 | SoT truth · spec · supersede fałszywych SEAL handoffów |
| S1 | `data/demand-os/set-now-sanitized/` · sync script · `.env.example` · readonly test |
| S2 | AB/CD layout · Money Check · stale/WoW/PREP/channel · desk-dash03 |
| S3 | skeleton · retry · keyboard · responsive · viewer RBAC |
| S4 | golden render · hunt SENT · hitl persist · 75 pytest |
| S5 | E2E flow static · `DESK-PHONE-SMOKE-CHECKLIST.md` |
| S6 | Campus map/program · scorecard · ASSET-MATERIALS · demand-os-execute |
| S7 | ten CLOSE · STATE update · **bez deploy** |

## Kluczowe fixy kodu

- `agent/demand_os/hunt_dry.py` — `allowlist_path` + `log_path` z `set_now_path()` (SENT badge)
- `commander-ui/` — layout AB/CD · UX states · desk-dash03
- `tests/` — golden · hunt · hitl · readonly · e2e flow

## Verify (replay)

```bash
DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized python tools/demand_os_hub.py doctor
DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized python -m pytest \
  tests/unit/test_demand_desk_ui_contracts.py \
  tests/test_demand_desk_api_extended.py \
  tests/test_demand_os_api_desk.py \
  tests/test_demand_os_desk_contract.py \
  tests/test_hunt_dry_updates_queue.py \
  tests/test_hitl_decision_persists.py \
  tests/unit/test_render_desk_golden.py \
  tests/unit/test_demand_os_status_readonly.py \
  tests/e2e/test_demand_desk_flow.py \
  tests/unit/test_commander_complete_ui.py \
  tests/unit/test_vhq_firm_ia_contracts.py -q
```

**Wynik lokalny:** 75 passed.

## Dowódca — next (human gate)

1. ~~**`GO DEPLOY COMMANDER UI`**~~ — **DONE @ f0fcbe7** (2026-08-02)
2. ~~sync set-now~~ — **DONE** → `/opt/jadzia/data/demand-os/set-now`
3. Env: `DEMAND_OS_SET_NOW` · `DEMAND_OS_MEMORY` — **SET** on VPS
4. Prod URL: `https://api.zzpackage.flexgrafik.nl/commander/?view=demand-desk&cb=desk-dash03`
5. Phone smoke: [`DESK-PHONE-SMOKE-CHECKLIST.md`](../ops/demand-os/DESK-PHONE-SMOKE-CHECKLIST.md)
6. Design §8 — 7 checkboxów w [`DEMAND-CONTROL-PANEL-DESIGN.md`](../ops/demand-os/DEMAND-CONTROL-PANEL-DESIGN.md) **tylko po prod**
7. Po §8 PASS → update STATE `tool_100 UI SEALED` · Hard DoD 15/15

## STOP

- `GO MARKETING HITL` · live publish · Ads · VPS bez GO
- Fałszywy SEAL przed Dowódca §8
