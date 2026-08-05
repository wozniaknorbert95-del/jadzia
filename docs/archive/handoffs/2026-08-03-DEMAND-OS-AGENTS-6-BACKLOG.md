---
gate: DEMAND-OS-MARKETING-4-00 · agents backlog MASTER-TODO-6
date: 2026-08-03
scope: tool-only · live marketing PARKED
---

# Handoff — MASTER-TODO-6: 10 zadań agents tool 100% (DONE)

## Co zrobiono (10/10)

| ID | Deliverable |
|----|-------------|
| 6-01 | STATE.md/todo.json/pointer sync: prod tip `74683e2` · `desk-dash11` · active_item `4-TOOL-AGENTS-6-01` |
| 6-02 | `docs/ops/demand-os/MASTER-TODO-6.md` — gate + backlog + DoD |
| 6-03 | Heartbeat per rola: `agents/heartbeat.py` (file SoT `AGENTS-HEARTBEAT.json`, env `DEMAND_OS_AGENTS_HEARTBEAT`) · `hub agents heartbeat --role` (RBAC act-class) · `list_agents()` pokazuje last_run/stale (>7d) |
| 6-04 | `demand_os_owner_verify.py` += agents registry contract + wave-check → 7 kroków, exit 0 |
| 6-05 | Coverage agents modules: **92% total, min moduł 82%** → `k12-coverage-agents.txt/json` + K-register note |
| 6-06 | `agents flow --apply` → calendar bind: slot `validated` + request_id + pass_token (idempotent re-bind) |
| 6-07 | `agents flow` += B.4 fatigue step przed CF brief (soft warn, nie blokuje chain) |
| 6-08 | wave-check W4 real checks: episodic keys + fatigue probe + A2A bus file (read-only) |
| 6-09 | GA4 inline credentials contract: `GA4_CREDENTIALS_JSON` liczy się tylko gdy inline JSON (`{…}`); path/garbage ≠ live (test) + coverage doc note |
| 6-10 | Desk tile **Agenci Demand OS**: `demand_agents` w status payload + sekcja UI + chips (narzędzie/brama live/stale) + `desk-dash12` (HTML+SW) + kontrakt `test_desk_agents_tile_contract` |

## Bugfix znaleziony w trakcie

- `wave_check.py`: blok `if wave == 4` był zagnieżdżony w `if wave == 3` → W4 checks nigdy się nie wykonywały. Naprawiono + regression test w `test_wave_readiness_shape_and_split`.

## Testy / verify

- `pytest tests/unit -k 'agents or ga4 or desk or pointer'` → **122 passed** (scope sweep)
- Pełna `tests/unit`: 672 passed, 10 failed — **wszystkie pre-existing** (vhq-w68a/dash09 stale cache asserts; chat/design_agent/facebook/dependencies z niecommitowanych zmian `agent/inspire/*` spoza scope)
- `commander_release.py validate` → ok, cache `desk-dash12`
- `demand_os_owner_verify.py` → exit 0 (doctor · pointer · pytest · footer · go_day · agents contract · wave-check)

## Uwagi

- `AGENTS-HEARTBEAT.json` = runtime state (nie commitowany) — zaczyna pusty po deploy, honest
- `DEMAND_OS_LEDGER` / `DEMAND_OS_CONTENT_CALENDAR` env overrides dodane dla izolacji testów (analogicznie do A2A/heartbeat)
- `shell: true` zostaje — worker loop per rola = osobny gate (NEXT w MASTER-TODO-6)

## RECOMMENDED_NEXT (tool)

1. Deploy `desk-dash12` → desk pokazuje sekcję Agenci
2. Worker loop per rola (design przed kodem) → dopiero wtedy `shell:false`
3. GA4 live: credentials (plik SA lub inline JSON) na VPS + `DEMAND_OS_GA4_LIVE=1` — po GO
