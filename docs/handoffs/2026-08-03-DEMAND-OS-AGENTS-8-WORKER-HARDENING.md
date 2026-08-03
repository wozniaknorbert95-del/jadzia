# Handoff — MASTER-TODO-8: Agents worker loop + hardening wave (2026-08-03)

**Zakres:** 10 zadań 8-01..8-10 · start od weryfikacji 7-ki · pełny cykl: verify → fix → test → commit → deploy → VPS verify.

## Wynik

| # | Zadanie | Status | Dowód |
|---|---------|--------|-------|
| 8-01 | Weryfikacja 7-ki (VPS+local full suite, hermetic dotenv) | DONE | VPS 688/0 · local 693/0 · commity `234d57a`, `c60ce52` |
| 8-02 | Working-tree hygiene (5F data, drift discard) | DONE | `3dc7164` |
| 8-03 | GDrive connector live fail-closed | DONE | `gdrive_cf.py` real client + 7 testów |
| 8-04 | Worker loop per rola (design → impl) | DONE | `agents/worker.py` + `run-due` (hub+CLI) + RBAC `agents-run-due` + systemd `.service`/`.timer` + 6 testów |
| 8-05 | Heartbeat staleness → wave-check | DONE | check `heartbeat_staleness` we wszystkich falach · limity 2×CADENCE · env override `DEMAND_OS_HB_STALE_<ROLE>` · 3 testy + dogfood red/green |
| 8-06 | Writable-path suite writerów | DONE | check `state_writers_resolvable` (9 writerów, real probe) · migracja `memory.py`+`heartbeat.py` na `state_paths` (jedna ścieżka kontraktu) · 2 testy |
| 8-07 | Coverage gate agents ≥80% | DONE | `test_agents_coverage_gate.py` · registry 93.6 / flow 90.8 / wave_check 97.8 / heartbeat 92.5 / worker 94.7 / wave1 88.3 · evidence `k12-coverage-agents.{json,txt}` |
| 8-08 | Desk staleness chip | DONE | chip `dziś/Nd/nigdy` z pasami fresh≤2d / aging≤7d / stale · payload `age_days` · cache **`desk-dash13`** · fixtures · 64 testy desk |
| 8-09 | SoT tip pointer check | DONE | `test_sot_tip_pointer.py` · prod_tip ∈ {HEAD, HEAD~1} na czystym tree · skip na dirty tree / untracked |
| 8-10 | Ship (verify+commit+deploy+VPS verify) | DONE | ten handoff + SoT sync + raport |

## Kontrakty dodane w 8-ce

1. **Worker loop** (`agents/worker.py`): jeden timer systemd (15 min) → `run-due` dispatchuje cadence-due akcje. CADENCE map: growth_lead 24h, sales 6h, validator/icp_brain/cre 24h. **Tool-only na zawsze**: live_gated role nigdy nie wchodzą do workera (live = HITL). Dry-run domyślnie; mutating akcje dostają `dry_run` z flagi `--apply`.
2. **Staleness**: wave-check raportuje stale gdy heartbeat starszy niż 2× cadence (never = stale). Detail zawiera komendę naprawczą.
3. **Writers**: wszystkie 9 runtime writerów przechodzi real write-probe w wave-check.
4. **Coverage**: agents package nie może spaść poniżej 80% line (gate w suite).
5. **Tip pointer**: STATE.md `prod_tip` mechanicznie pilnowany względem HEAD.

## Testy

- local: `tests/unit` **714 passed, 0 failed** · `tests/` root **336 passed**
- agents-focus suites: 22/22 (flow+wave+worker) · coverage gate 2/2
- VPS owner-verify po deploy: patrz sekcja Post-deploy poniżej

## Ryzyka / decyzje

- **Heartbeat per-rola, nie per-akcja**: run-due dispatchuje wszystkie due akcje roli w jednej turze (money_check+sync_starts razem) — świadome uproszczenie, udokumentowane w `AGENTS-WORKER-LOOP-DESIGN.md`.
- **Desk chip progi** (2d/7d) są UI-owe; wave-check staleness używa 2×CADENCE — dwie skale, jeden kierunek (fresh=good).
- Timer systemd: pliki w `deployment/` — **aktywacja na VPS dopiero po decyzji Dowódcy** (worker zmienia stan: sync_starts/sync_hot/sync_memory zapisują SoT-side pliki; dry domyślnie w CLI, ale timer biegnie z `--apply`).

## Post-deploy prod verify

- VPS HEAD = **`0930ea6`** (ff-only; commity `44a7166` kod + `0930ea6` SoT/handoff).
- Deploy hiccup: merge jako `root` zostawił 114 plików root-owned → 2× PermissionError (`CONTROL-AUDIT.jsonl`, desk HITL testy). Fix: `chown -R jadzia:jadzia /opt/jadzia` (0 pozostało). **Lekcja (jak D8-05): VPS `git merge` zawsze `sudo -u jadzia`** — dopisać do deploy playbook.
- Owner-verify: **`ok:true`, errors []** — doctor ✓ pointer ✓ pytest demand_os 114/0 ✓ footer ✓ go_day ✓ waves 1–4 `tool_ready`.
- Full unit na prod: **709 passed, 0 failed, 22 skipped** (skips = env by design: inspire sibling, GA4 live creds).
- Wave-check prod: `heartbeat_staleness` ok (all cadence roles fresh) · `state_writers_resolvable` **9/9** ok.
- `run-due` prod dry: ok, due=[] (heartbeats świeże z dispatchów dogfood).
- Service: `systemctl restart jadzia` → active, `/health` 200.
- SoT: STATE/current-task/todo.json → tip `0930ea6` (STATE wskazuje deploy-tip `0930ea6`; kod-tip `44a7166` w HEAD~1 — pointer test toleruje oba).

## Następny cykl (MASTER-TODO-9, po unlock decyzji)

1. Weryfikacja 8-ki na prod (staleness zielone po pierwszym przebiegu timera).
2. Decyzja Dowódcy: aktywacja timera workera (Zasada 11) **lub** dalej ręczne `run-due`.
3. Live P0 nadal PARKED — bez zmian (`UNLOCK-LIVE-P0.md`).
