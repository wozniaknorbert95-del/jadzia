# HANDOFF — PUNCH LISTA C + POST-CODING SHIP (2026-08-05)

**Date:** 2026-08-05
**Scope:** punch lista C1–C8 z [MARATON-678-VERIFICATION-AUDIT](./2026-08-03-MARATON-678-VERIFICATION-AUDIT.md) + ship
**Prod tip:** `b53e063` (+ SoT `a84ddcd`) · cache `desk-dash13` · **owner-verify ok:true**
**Live marketing:** PARKED (bez zmian)

## Werdykt

**10/10 kroków planu DONE, każdy z dowodem.** Worker loop przeszedł z "kod w repo" do **LIVE timer na prod** (15-min cykl). Dwa nowe defekty znalezione w trakcie baseline/E2E (D9-01, D9-02) — oba naprawione z testami regresji. Live P0 nadal PARKED.

## Dowody per krok

| # | Krok | Dowód |
|---|------|-------|
| 1 | Baseline verify | Local/VPS `edfd305` parity · unit 714/0 + 709/0 · **D9-01 wykryty** (staleness self-defeating) |
| 2 | C2 security | `62f5769` gitignore secrets/output/.superpowers/assets + scoped GROWTH-EVENTS · VPS `" "` usunięty · `check-ignore` dowód · 0 root-owned |
| 3 | C3 playbook | `6646957` — `jadzia-deploy.md`: VPS git = `sudo -u jadzia` + `find ! -user jadzia` gate == 0 |
| 4 | C1 timer (GO) | `systemctl enable --now demand-os-agents-worker.timer` · pierwszy cykl 09:21 SUCCESS · kontrolowany dispatch sales (backdate −7h → due → dispatched=2, errors=0) · staleness green z realnego biegu · D9-01 fix `10f5f9f` · shell:false flip 5 ról cadence `143d45e` |
| 5 | C4 stash ×9 | 9/9 **drop** po review `show --stat`/`show -p` — treść każdego w HEAD lub regenerowalna (tabela poniżej) · `git stash list` pusta |
| 6 | C5 evidence gate | `81a8fe1` — `JADZIA_EVIDENCE_WRITE=1` gate ×2 testy + conftest state-tmp fixture (9 writerów → per-test tmp, seed MEMORY/calendar) · pełny suite zostawia **czyste tree** (local + VPS) |
| 7 | C6 higiena | artifact GROWTH-EVENTS usunięty lokal+VPS · plan os-target zarchiwizowany `5e395e6` · local+VPS tree czyste |
| 8 | C7 docs+testy | `a02c3ae` — owner-verify pack += coverage gates · doctor `agents_staleness` advisory + test · RBAC viewer-blocked run-due (apply+dry) · **D9-02 fixed** (`2b4ad6b` hub dotenv + 8 env overrides prod) · E2E browser prod: [screenshot](./evidence/c7-e2e-2026-08-05/desk-agents-live-prod.png) — `dziś / bieg: 2026-08-05` |
| 9 | Ship | Local root **1055/0** · VPS unit **712/0** · owner-verify **ok:true** (7/7 kroków) · tip pointer green obie strony · każdy deploy: ff-only `sudo -u jadzia`, find-gate 0 |
| 10 | MT-9 + close | [`MASTER-TODO-9.md`](../ops/demand-os/MASTER-TODO-9.md) (10 zadań, #1 = verify workera 2026-08-12) · S-register zamknięty (B2 w audit handoff) |

## C4 — tabela decyzji stashy (9/9 drop)

| Stash | Treść | Decyzja | Uzasadnienie |
|-------|-------|---------|--------------|
| @{0} runtime drift pre-8-deploy | k12 coverage + CONTROL-AUDIT + MEMORY | drop | regenerowalne (S7 potem wyeliminował klasę) |
| @{1} drift-aug3b | conftest hermetic + testy + handoff 5F + todo | drop | treść w HEAD (`c60ce52`, `4041dbf`) |
| @{2} drift-aug3 | sanitized MEMORY +44 | drop | runtime memory drift |
| @{3} line-ending pre-b1e6e26 | 346 plików, 57k linii ± | drop | CRLF normalization |
| @{4} agent-temp | tool-first pointer 69+/69− | drop | whitespace; wersja w HEAD przechodzi suite |
| @{5} temp-fb-scripts | fb token `_load_env_into_os()` +2 | drop | już w HEAD (linia 97) |
| @{6} queue-clean-20260717 | 141 plików line-endings | drop | normalization |
| @{7} pre-coi-commander-20260709 | 89 plików line-endings | drop | normalization |
| @{8} pre-int012-deploy | 122 pliki line-endings | drop | normalization |

## Nowe defekty znalezione i naprawione (poza planem)

- **D9-01** staleness self-defeating: wave-check probes auto-heartbeatiły role przed pomiarem → check zawsze green. Fix: `dispatch(probe=True)` nie zapisuje heartbeat; regresje: probe-never-records + wave-check-nie-rusza-pliku.
- **D9-02** split-brain runtime paths: app (`ProtectSystem=strict`, ReadWritePaths bez docs/) → fallback `data/`; worker/CLI (pełne prawa) → repo set-now. Desk pokazywał plik z Aug-3. Fix: hub ładuje `.env` (jak core/services) + 8 `DEMAND_OS_*` overrides w prod `.env` → jeden canonical path `data/demand-os/set-now/`. Migracja najświeższych plików wykonana.
- **owner-verify contract**: assertował `shell=True` dla wszystkich — zaktualizowany do `_WORKER_CADENCE_ROLES` (registry = single source).

## Stan końcowy

- prod `a84ddcd` (tip `b53e063` w STATE = HEAD~1 pattern ✓) · service active · timer active (nast. tick co 15 min)
- VPS tree czyste · stash puste · 0 root-owned
- Suites: local 1055/0 · VPS 712/0 · owner-verify ok:true
- Desk prod: sekcja Agenci live, chip `dziś`, dash13

## Następna sesja

→ [`MASTER-TODO-9.md`](../ops/demand-os/MASTER-TODO-9.md) — zadanie 1 (2026-08-12): tygodniowa weryfikacja workera (journal audit, cadence fakty vs mapa, staleness trend).
Live P0: **PARKED** do UNLOCK Dowódcy.
