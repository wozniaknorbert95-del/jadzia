# MASTER TODO 7 — Weryfikacja + Hardening (agents tool 100%)

**Status:** ✅ **10/10 DONE** (sesja 2026-08-03, druga iteracja)
**Kierunek:** tool-only; live marketing PARKED (hard lock `.cursor/rules/demand-os-tool-first.mdc`)

## Definicja sesji

Zaczynamy od **dogłębnej weryfikacji** poprzedniej 10-ki (MASTER-TODO-6), nie od nowych
ficzerów. Znalezione defekty naprawiamy z testami regresyjnymi; pre-existing failures
rozliczamy do zera; kończymy ship (commit + deploy).

## Rejestr defektów znalezionych w weryfikacji (7-01)

| ID | Defekt | Fix |
|----|--------|-----|
| D1 | Heartbeat był manual-only → martwy mechanizm | auto-heartbeat w `dispatch()` (best-effort, fail nie zapisuje) + test |
| D2 | `agents flow --channel myspace` → `UtmLockError` crash CLI | `run_hub_spoke_flow` nigdy nie rzuca — honest envelope `flow_exception` + test |
| D3 | `flow --apply` cross-channel: bind fb nadpisywał slot tt (match tylko po asset_id) | `set_slot_status(..., channel=)` filtr + flow przekazuje channel + test (2 sloty/asset) |

## Backlog (10/10)

| ID | Zadanie | Status | Dowód |
|----|---------|--------|-------|
| 7-01 | Dogłębna weryfikacja 6-xx (edge cases: dispatch/heartbeat/flow/calendar/stale boundary/W4) | ✅ | rejestr D1-D3 wyżej; skrypt audytowy 11/11 PASS po fixach |
| 7-02 | Auto-heartbeat w dispatch (D1) | ✅ | `registry._record_run_heartbeat`; test `test_dispatch_records_auto_heartbeat`; VPS dogfood `hb_roles=['validator']` |
| 7-03 | Stale cache asserts (desk-dash06/vhq-w68a x2) | ✅ | cache-agnostic consistency: HTML `?v=tag` ↔ SW `coi-commander-{tag}` (3 testy przepisane) |
| 7-04 | Pre-existing failures: JWT K3 signature, TikTok platform contract, external brain copy coupling, generate rate-limit isolation | ✅ | 6 testów naprawionych; **pełna suita 687→688 passed, 0 failed** (pierwszy raz zielona) |
| 7-05 | Working tree: offerte T-012 (WIP +34) + test fail-safe; `AGENTS-HEARTBEAT.json` gitignore (runtime state) | ✅ | `test_create_offerte_analytics_fail_safe`; mp4/log/.superpowers świadomie untracked |
| 7-06 | Desk tile Agenci — E2E browser dogfood | ✅ | 9 wierszy, chips `brama live`/`narzędzie`, `bieg: 2026-08-03` (auto-heartbeat), screenshot; API 200; public endpoint auth-gated (`detail`) |
| 7-07 | Flow dogfood na VPS (dry + apply + per-channel + auto-hb + invalid) na tmp paths | ✅ | DRY calendar skipped · APPLY added · fb+tt 2 sloty · INVALID=flow_exception · cleanup tmp |
| 7-08 | Hardening: `cal_step.request_id` w output; coverage re-run | ✅ | agents modules **90% total, min 82%** → `k12-coverage-agents.txt/json` |
| 7-09 | Desk MCP honesty (GA4/GDrive) | ✅ (już pokryte) | GA4 „czeka" w sekcji SEO; `blocked_reason` per rola; coverage doc G.2/G.3 — bez dublowania |
| 7-10 | Ship: verify + handoff + commit + deploy | ✅ | owner-verify exit 0 · release validate ok · 688+114 passed · VPS health 200 |

## Verify (final)

- `pytest tests/unit` → **688 passed, 16 skipped, 0 failed**
- `pytest tests/ -k demand_os` → 114 passed
- `tools/demand_os_owner_verify.py` → exit 0 (7 kroków)
- `tools/commander_release.py validate` → ok (cache `desk-dash12`, bez zmian UI → bez bumpu)
- Lint: 3 nowe UP-preferencje (styl zgodny z modułem; repo nie gate'uje pyupgrade)

## Uwagi

- Auto-heartbeat to telemetria przy każdym udanym dispatch — read-action może pisać heartbeat (jak audit log), nie łamie RBAC.
- `AGENTS-HEARTBEAT.json` = runtime per-env state (gitignored od tej sesji).
- Testy design-agent nie mogą wiązać się z literalnym copy z `flexgrafik-inspire` brain (rotuje niezależnie) — kotwice strukturalne (`missing_fields`, golden path v6.1).
