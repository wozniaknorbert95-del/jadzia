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
| 1 | 9-01 | **1** (2026-08-12) | **Weryfikacja workera po tygodniu** | Journal audit: `journalctl -u demand-os-agents-worker.service --since -7d` — każdy tick rc=0 · faktyczny cadence per rola vs CADENCE map (tabela) · staleness trend (7 snapshotów wave-check) · zero `errors>0` |
| 2 | 9-09 | ~~2~~ **DONE 2026-08-05** | **Blocking-mode canary na prod** (nowe, z self-auditu G1) | ✅ [`2026-08-05-MT9-09-CANARY-CLOSE.md`](../handoffs/2026-08-05-MT9-09-CANARY-CLOSE.md): backdate sales −8d → doctor RED `sales(194.2h>12h) [blocking]` + owner-verify exit 1 + desk footer `doctor_ok:false` → restore → green · okno 2:26 < 5 min |
| 3 | 9-02 | **3** | Desk chip stale vs cadence limits (S10) | `heartbeat_view.stale` (STALE_DAYS=7) używa limitów per-rola z wave_check (`_STALE_LIMITS_H`) lub wspólnego źródła · chip `stale` na desk zgodny z wave-check · test kontraktu |
| 4 | 9-03 | **4** | Worker journal → evidence snapshot | Cotygodniowy eksport `journalctl` do `docs/handoffs/evidence/worker/` (skrypt + cron/timer albo manualny krok w 9-01) · evidence w handoffie |
| 5 | 9-04 | **5** | `agents run-due` dry w desk diagnostics | Desk "Diagnostyka" pokazuje `due=[]/due=[...]` read-only (bez dispatch) · test UI kontraktu |
| 6 | 9-05 | **6** | Coverage gate: `worker.py` per-module floor 90% | Worker jest sercem pętli — podnieść floor dla niego · evidence refresh |
| 7 | 9-06 | **7** | Alert path dla worker failure — decyzja po G1 | Doctor blocking już failuje gdy stale (prod). Zdecydować: czy `OnFailure=`/Telegram notify dodaje wartość ponad doctor RED + desk footer · decyzja + implementacja albo dokument "doctor wystarcza" |
| 8 | 9-07 | **8** | `shell:false` dla tt/cf/fb/blog — kryteria exit | Zdefiniować co musi istnieć (flow auto? HITL desk action?) żeby flip był uczciwy · dokument decyzji (nie implementacja flow) |
| 9 | 9-08 | **9** | MASTER-TODO-6/7/8 verification sweep #2 | Po tygodniu workera: rerun asercji A1-A15 z maraton audit · nowe D-numery dla znalezisk |
| 10 | 9-10 | **10** | Upkeep: tip pattern + S-register + handoff tygodniowy | Dopisać do `.agents/workflows/jadzia-deploy.md` pattern "prod_tip = HEAD~1 po SoT sync" (dawne 9-09) · po 9-01: aktualizacja rejestru S1-S15 + nowe skróty · handoff w `docs/handoffs/` |

## STOP (bez zmian)

- Live P0 / Ads / publish — PARKED do UNLOCK Dowódcy
- VPS git tylko `sudo -u jadzia` (playbook gate: `find /opt/jadzia ! -user jadzia` == 0)
- Żaden `git add -A` na VPS (secrets/ output/ są gitignore, ale zasada stoi)
- Canary 9-09 = jedyna dozwolona manipulacja runtime na prod; okno < 5 min, restore natychmiast
