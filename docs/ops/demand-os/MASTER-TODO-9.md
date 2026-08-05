---
status: ACTIVE
updated: "2026-08-05"
pack: AGENTS-9
parent: MASTER-TODO-8.md (DONE)
tool_first: marketing live P0 PARKED — ten plik dotyczy WYŁĄCZNIE narzędzia
---

# MASTER-TODO-9 — Agents steady-state + verification (10 zadań)

**Wejście (refresh po self-audicie):** worker timer LIVE (15 min) · punch lista C1–C8 DONE ·
self-audit G1–G9 FIXED · **doctor staleness = hard gate na prod** (`DEMAND_OS_STALENESS_BLOCKING=1`) ·
prod `a892ce0` owner-verify ok:true (blocking mode).
**Zasada:** każde zadanie domykane dowodem (test/log/journal), nie deklaracją.
**Kolejność** = rekomendowany porządek wykonania (senior review 2026-08-05).

## Zadania

| # | ID | Kolejność | Temat | DoD |
|---|----|-----------|-------|-----|
| 1 | 9-01 | **1** (2026-08-12) | **Weryfikacja workera po tygodniu** | Journal audit: `journalctl -u demand-os-agents-worker.service --since -7d` — każdy tick rc=0 · faktyczny cadence per rola vs CADENCE map (tabela) · staleness trend (7 snapshotów wave-check) · zero `errors>0` · **interim 2026-08-05:** 37 ticków, 0 failures, wszystkie role fresh (age 2.6-8.8h vs cadence 6-24h) · narzędzie: `tools/demand_os_worker_journal_export.py` |
| 2 | 9-09 | ~~2~~ **DONE 2026-08-05** | **Blocking-mode canary na prod** (nowe, z self-auditu G1) | ✅ [`2026-08-05-MT9-09-CANARY-CLOSE.md`](../handoffs/2026-08-05-MT9-09-CANARY-CLOSE.md): backdate sales −8d → doctor RED `sales(194.2h>12h) [blocking]` + owner-verify exit 1 + desk footer `doctor_ok:false` → restore → green · okno 2:26 < 5 min |
| 3 | 9-02 | ~~3~~ **DONE 2026-08-05** | Desk chip stale vs cadence limits (S10) | ✅ Wspólne źródło: `heartbeat.STALE_LIMITS_H` + `stale_limit_hours()` (env override > tabela > default) — `heartbeat_view` i `wave_check` używają jednej polityki · desk rows eksponują `stale_limit_h` · test kontraktu `test_desk_chip_matches_wave_staleness` + 2 kolejne · S-register S10 → FIXED |
| 4 | 9-03 | ~~4~~ **DONE 2026-08-05** | Worker journal → evidence snapshot | ✅ `tools/demand_os_worker_journal_export.py` (parser pure-function, 3 testy; realny format "Starting" złapany w regresji) → `docs/handoffs/evidence/worker/worker-journal-YYYY-MM-DD.md` · pierwszy eksport przy deploy · krok w 9-01 |
| 5 | 9-04 | ~~5~~ **DONE 2026-08-05** | `agents run-due` dry w desk diagnostics | ✅ `diagnostics.agents_due` w desk status (count/items/mode=read_only/source) — desk Diagnostyka pokazuje JSON automatycznie · 3 testy kontraktu (`test_agents_due_*`) w tym dowód read-only (status build nie pisze heartbeatów) |
| 6 | 9-05 | ~~6~~ **DONE 2026-08-05** | Coverage gate: `worker.py` per-module floor 90% | ✅ `MODULE_FLOORS` w gate: worker **90%** (faktycznie **100%** po teście defensywnych branchy live_gated/action-missing) · evidence `k12-coverage-agents.txt` refresh · reszta modułów 88-98% |
| 7 | 9-06 | **7** | Alert path dla worker failure — decyzja po G1 | Doctor blocking już failuje gdy stale (prod). Zdecydować: czy `OnFailure=`/Telegram notify dodaje wartość ponad doctor RED + desk footer · decyzja + implementacja albo dokument "doctor wystarcza" |
| 8 | 9-07 | **8** | `shell:false` dla tt/cf/fb/blog — kryteria exit | Zdefiniować co musi istnieć (flow auto? HITL desk action?) żeby flip był uczciwy · dokument decyzji (nie implementacja flow) |
| 9 | 9-08 | **9** | MASTER-TODO-6/7/8 verification sweep #2 | Po tygodniu workera: rerun asercji A1-A15 z maraton audit · nowe D-numery dla znalezisk |
| 10 | 9-10 | **10** (część DONE) | Upkeep: tip pattern + S-register + handoff tygodniowy | ✅ 2026-08-05: tip convention (prod_tip=HEAD~1) + reguła "pytest na VPS też jako jadzia" dopisane do `jadzia-deploy.md` · S-register S10 → FIXED · po 9-01: pełny sweep rejestru + handoff tygodniowy |

## STOP (bez zmian)

- Live P0 / Ads / publish — PARKED do UNLOCK Dowódcy
- VPS git tylko `sudo -u jadzia` (playbook gate: `find /opt/jadzia ! -user jadzia` == 0)
- Żaden `git add -A` na VPS (secrets/ output/ są gitignore, ale zasada stoi)
- Canary 9-09 = jedyna dozwolona manipulacja runtime na prod; okno < 5 min, restore natychmiast
