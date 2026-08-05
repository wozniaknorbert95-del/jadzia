---
status: ACTIVE
updated: "2026-08-05"
pack: AGENTS-9
parent: MASTER-TODO-8.md (DONE)
tool_first: marketing live P0 PARKED — ten plik dotyczy WYŁĄCZNIE narzędzia
---

# MASTER-TODO-9 — Agents steady-state + verification (10 zadań)

**Wejście:** worker timer LIVE (2026-08-05, `demand-os-agents-worker.timer`, 15 min) ·
punch lista C1–C8 DONE · prod `b53e063` owner-verify ok:true.
**Zasada:** każde zadanie domykane dowodem (test/log/journal), nie deklaracją.

## Zadania

| # | ID | Temat | DoD |
|---|----|-------|-----|
| 1 | 9-01 | **Weryfikacja workera po tygodniu** (termin: 2026-08-12) | Journal audit: `journalctl -u demand-os-agents-worker.service --since -7d` — każdy tick rc=0 · faktyczny cadence per rola vs CADENCE map (tabela) · staleness trend (7 snapshotów wave-check) · zero `errors>0` |
| 2 | 9-02 | Desk chip stale vs cadence limits | `heartbeat_view.stale` (STALE_DAYS=7) używa limitów per-rola z wave_check (`_STALE_LIMITS_H`) lub wspólnego źródła · chip `stale` na desk zgodny z wave-check · test kontraktu |
| 3 | 9-03 | Worker journal → evidence snapshot | Cotygodniowy eksport `journalctl` do `docs/handoffs/evidence/worker/` (skrypt + cron/timer albo manualny krok w 9-01) · evidence w handoffie |
| 4 | 9-04 | `agents run-due` dry w desk diagnostics | Desk "Diagnostyka" pokazuje `due=[]/due=[...]` read-only (bez dispatch) · test UI kontraktu |
| 5 | 9-05 | Coverage gate: `worker.py` per-module floor 90% | Worker jest sercem pętli — podnieść floor dla niego · evidence refresh |
| 6 | 9-06 | Alert path dla worker failure | Timer `OnFailure=` → notify (Telegram/ledger) albo documented fallback: wave-check RED wystarcza? Decyzja + implementacja/dokument |
| 7 | 9-07 | `shell:false` dla tt/cf/fb/blog — kryteria exit | Zdefiniować co musi istnieć (flow auto? HITL desk action?) żeby flip był uczciwy · dokument decyzji (nie implementacja flow) |
| 8 | 9-08 | MASTER-TODO-6/7/8 verification sweep #2 | Po tygodniu workera: rerun asercji A1-A15 z maraton audit · nowe D-numery dla znalezisk |
| 9 | 9-09 | Sot tip pointer: tolerancja HEAD~N? | Przy częstych SoT2 commitach rozważyć HEAD~2 albo dokumentację patternu "tip=HEAD~1 zawsze" w playbooku deploy |
| 10 | 9-10 | Handoff tygodniowy + S-register upkeep | Po 9-01: aktualizacja rejestru S1-S15 + nowe skróty · handoff w `docs/handoffs/` |

## STOP (bez zmian)

- Live P0 / Ads / publish — PARKED do UNLOCK Dowódcy
- VPS git tylko `sudo -u jadzia` (playbook gate: `find /opt/jadzia ! -user jadzia` == 0)
- Żaden `git add -A` na VPS (secrets/ output/ są gitignore, ale zasada stoi)
