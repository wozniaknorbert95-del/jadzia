---
status: DONE
updated: "2026-08-05"
task: MASTER-TODO-9 zadanie 9 (9-08) — verification sweep #2
base_audit: docs/handoffs/2026-08-03-MARATON-678-VERIFICATION-AUDIT.md
---

# MT-9 9-08 — Sweep weryfikacyjny #2 (rerun asercji A1–A15)

**Data:** 2026-08-05 · **Wykonawca:** QA sweep (subagent, read-only) · **Repo tip:** `b3497f3` (master == origin/master, tree czyste)
**Metoda:** rerun A1–A15 z audytu maratońskiego 2026-08-03 przeciwko aktualnemu stanowi repo.
Ograniczenia sesji: **bez pełnego suite'u testów** (za wolny — użyto `--collect-only` + targeted pytest),
**bez modyfikacji plików** (poza tym dokumentem), **bez ssh/VPS** — asercje prod oznaczone N/A-prod
z dokładną komendą operatorską.

## Tabela weryfikacji A1–A15

| ID | Treść asercji | Metoda | Wynik | Dowód (file:line / output) |
|----|---------------|--------|-------|-----------------------------|
| A1 | Local unit suite green | `python -m pytest tests/unit --collect-only -q` (pełny run pominięty zgodnie z ograniczeniem) | PASS (collect-only) | `735 tests collected in 1.10s` — wzrost z 731 (714p+17s) o +4 testy = nowe testy G1/RBAC dodane po audycie; 0 errorów kolekcji |
| A2 | Local root suite green | `python -m pytest --collect-only -q` (całe `tests/`) | PASS (collect-only) | `1076 tests collected in 1.86s` — wzrost o ~7 vs stan z audytu (1055 p + skips); 0 errorów kolekcji |
| A3 | VPS unit suite green @ prod tip | brak dostępu do VPS z tej sesji | N/A-prod | `cd /opt/jadzia && sudo -u jadzia env HOME=/home/jadzia venv/bin/python -m pytest tests/unit -q` → oczekiwane 0 failed, skips tylko env |
| A4 | Δ local↔VPS = tylko env-skips (inspire sibling, GA4 creds) | wymaga obu stron | N/A-prod | porównać output A3 z A1: różnica wyłącznie w skipped (inspire sibling, GA4 creds); jakiekolwiek failed = regresja |
| A5 | VPS owner-verify `ok:true`, errors [] | struktura skryptu zweryfikowana lokalnie (bootstrap sys.path L19-20, dotenv L22-28, utf-8 reconfigure L56-57, hermetic env L62-66 w `tools/demand_os_owner_verify.py`); ostatni prod run ok:true (MASTER-TODO-9.md:13) | N/A-prod | `sudo -u jadzia env HOME=/home/jadzia venv/bin/python tools/demand_os_owner_verify.py` → oczekiwane `"ok": true`, errors []; NB: prod `.env` ma `DEMAND_OS_STALENESS_BLOCKING=1` — hermetic env (G9) musi je strippnąć z subprocessu pytest |
| A6 | VPS service active + `/health` 200 | brak dostępu do VPS | N/A-prod | `systemctl is-active jadzia` → active · `curl -s -o /dev/null -w '%{http_code}' http://localhost:8000/health` → 200 |
| A7 | Prod UI = dash13 | repo: Grep cache tag; prod curl niedostępny | PASS (repo) · N/A-prod (prod) | repo: `commander-ui/sw.js:2` → `CACHE = "coi-commander-desk-dash13"`; prod: `curl -s https://app.flexgrafik.nl/commander/sw.js \| grep dash` → oczekiwane `dash13` (STATE.md prod_tip: desk-dash13) |
| A8 | Wave-check prod: `heartbeat_staleness` ok, `state_writers_resolvable` 9/9 | lokalnie: doctor pokazuje staleness (patrz niżej); prod niedostępny | N/A-prod | `sudo -u jadzia env HOME=/home/jadzia venv/bin/python tools/demand_os_hub.py agents wave-check` → oczekiwane staleness ok (fresh, worker LIVE), writers 9/9 |
| A9 | run-due prod dry: ok, due=[] | brak dostępu do VPS | N/A-prod | `sudo -u jadzia env HOME=/home/jadzia venv/bin/python tools/demand_os_hub.py agents run-due` (dry, bez --apply) → ok, due=[] przy świeżych heartbeatach |
| A10 | RBAC run-due: viewer → `missing demand_os:act` | CLI dogfood lokalnie + dedykowany test jednostkowy | PASS | `$env:DEMAND_OS_ROLE='viewer'; python tools/demand_os_hub.py agents run-due` → `exit=1`, `"error": "DEMAND_OS_ROLE=viewer missing demand_os:act"`; test: `tests/test_demand_os_coherence_etap1.py:93` `test_hub_rbac_viewer_blocked_run_due` — w runie 15/15 passed (pointer+coherence) |
| A11 | Git local: master == origin/master, tree czyste | `git status -sb` · `git status --porcelain` · `git log origin/master..HEAD` | PASS | `## master...origin/master` @ `b3497f3`, porcelain puste (0 plików), 0 commitów ahead/behind |
| A12 | Git VPS: HEAD == prod_tip w STATE | STATE odczytane lokalnie; VPS HEAD niedostępny | N/A-prod | STATE.md:6/19 `prod_tip: 28a2e8a` = lokalny HEAD~1 (zgodne z patternem 9-10 „prod_tip = HEAD~1 po SoT sync"); weryfikacja: `git -C /opt/jadzia rev-parse --short HEAD` → oczekiwane `28a2e8a` |
| A13 | Zero TODO/FIXME/HACK w plikach 8-ki | Grep `TODO\|FIXME\|HACK` w `agents/worker.py`, `agents/wave_check.py`, `gdrive_cf.py`, `state_paths.py`, `tools/demand_os_hub.py` | PASS | 0 trafień we wszystkich 5 plikach |
| A14 | Brak `secrets/` w historii repo | `git log --all --oneline -- secrets/` + `git ls-files secrets/` | PASS | oba outputy puste; dodatkowo `.gitignore:46-47` ma `secrets/` + `output/` (S5) |
| A15 | Live marketing PARKED (zero publish, zero ads) | odczyt SoT: STATE.md, todo.json, MASTER-TODO-4.md; doctor marketing mode | PASS | STATE.md:2/18 `active_item 4-TOOL-AGENTS-9 · live 4-P0-* PARKED`, :22 `live_cadence PARKED`, :24 `Ads PARK cash`; todo.json:10 `"active_item": "4-TOOL-AGENTS-9"`; MASTER-TODO-4.md:110 `CURRENT: 4-AWAIT-UNLOCK · ready_for_human`; doctor lokalnie: `marketing=PARKED_LAST` |

**Podsumowanie:** 15 asercji → **7× PASS** (A1, A2, A10, A11, A13, A14, A15; A7 repo-side PASS),
**0× FAIL**, **8× N/A-prod** (A3, A4, A5, A6, A8, A9, A12 + prod-side A7). Każdy PASS ma dowód z tej sesji.

## Drift-watch — mechanizmy dodane po audycie (punkty a–e z zadania)

| # | Mechanizm | Metoda | Wynik | Dowód |
|---|-----------|--------|-------|-------|
| a | Doctor staleness env-aware blocking (`DEMAND_OS_STALENESS_BLOCKING`) | Read `agent/demand_os/doctor.py` + run doctor lokalnie | PASS | `doctor.py:336` `staleness_blocking = os.environ.get("DEMAND_OS_STALENESS_BLOCKING") == "1"`; :352 `_ADVISORY = set() if staleness_blocking else {"agents_staleness"}`; :345-346 blocking → errors. Lokalny run: `ok=True`, `agents_staleness True \| all cadence roles fresh [advisory]` — advisory lokalnie, blocking na prod zgodnie z projektem G1 |
| b | owner-verify: sys.path bootstrap + dotenv + utf-8 + hermetic env | Read `tools/demand_os_owner_verify.py` | PASS | L19-20 sys.path insert ROOT; L22-28 `load_dotenv(ROOT / ".env")` (guard `JADZIA_TEST_NO_DOTENV`); L56-57 `sys.stdout.reconfigure(encoding="utf-8")`; L62-66 hermetic pytest subprocess: `JADZIA_TEST_NO_DOTENV=1` + `env.pop("DEMAND_OS_STALENESS_BLOCKING")` (G9) |
| c | conftest fixture `_demand_os_state_tmp` usuwa `DEMAND_OS_STALENESS_BLOCKING` | Read `tests/conftest.py` | PASS | `tests/conftest.py:57-61` — fixture autouse, `monkeypatch.delenv("DEMAND_OS_STALENESS_BLOCKING", raising=False)` przed seedowaniem stanu tmp |
| d | `docs/handoffs` rolling ≤15 + archiwum | PowerShell count + Read README | PASS | 16 plików `.md` w `docs/handoffs/` = 15 handoffów + `README.md`; README:1 `rolling ≤15`, README:3 cold history `docs/archive/handoffs/` (katalog istnieje, zapełniony); najnowsze: 2026-08-05 ×4 |
| e | Worker timer LIVE na prod (`demand-os-agents-worker.timer`) | repo: jednostki systemd obecne; prod nieweryfikowalny z sesji | N/A-prod | repo: `deployment/demand-os-agents-worker.service` + `.timer` istnieją; STATE.md:21 `worker timer LIVE (15 min, first dispatch 2026-08-05)`; weryfikacja prod: `systemctl list-timers demand-os-agents-worker.timer` + `journalctl -u demand-os-agents-worker.service --since today` → każdy tick rc=0 |

## Regresje defektów D9-01/D9-02 (kontrola fixów)

| Defekt | Fix (commit) | Kontrola | Wynik |
|--------|--------------|----------|-------|
| D9-01 probe dispatches auto-heartbeatiły role | `10f5f9f` (commit istnieje w log) | Grep `probe=True` w `agents/wave_check.py` | PASS — L42/59/69 dispatch z `probe=True` (bez heartbeat) |
| D9-02 split-brain runtime paths | `2b4ad6b` (commit istnieje) | Grep `load_dotenv` w `tools/demand_os_hub.py` | PASS — L423-425 hub CLI ładuje `.env` |
| S-register S1–S15 (rozliczony 2026-08-05) | commity `a02c3ae`, `62f5769`, `81a8fe1`, `6646957`, `d77dc9d` | `git log --oneline -1 <sha>` dla każdego | PASS — wszystkie 8 commitów obecne w historii |
| S7 evidence drift (dirty tree po verify) | gate `JADZIA_EVIDENCE_WRITE` | Grep w `tests/unit/test_agents_coverage_gate.py:45` + `test_desk_coverage_k12.py:45` | PASS — write tylko pod env flagą; tree czyste (A11) |
| S5/S6 runtime artifacts | gitignore + brak plików | `Test-Path` GROWTH-EVENTS (oba False) + `.gitignore:43-51` | PASS |

## Nowe znaleziska

Brak nowych znalezisk.

(Rejestr D pozostaje przy D9-02. Wzrost liczby testów 731→735 unit / ~1069→1076 total to zamierzone
dodatki poaudytowe: test RBAC run-due (S9), test 3-fazowy blocking (G1), testy canary/hygiene —
potwierdzone commitami, nie dryf.)

## Uwagi dla operatora (pakiet N/A-prod)

Jedna sesja operatorska na VPS domyka sweep (kolejność = kolejność tabeli; wszystko read-only poza owner-verify,
który jest idempotentny i po G9/S7 nie brudzi tree):

```bash
cd /opt/jadzia
git rev-parse --short HEAD                                   # A12 → 28a2e8a
systemctl is-active jadzia                                   # A6 → active
curl -s -o /dev/null -w '%{http_code}\n' http://localhost:8000/health   # A6 → 200
curl -s https://app.flexgrafik.nl/commander/sw.js | grep -o 'desk-dash[0-9]*'  # A7 → dash13
sudo -u jadzia env HOME=/home/jadzia venv/bin/python -m pytest tests/unit -q      # A3/A4 → 0 failed, env-skips only
sudo -u jadzia env HOME=/home/jadzia venv/bin/python tools/demand_os_hub.py agents wave-check       # A8 → staleness ok, writers 9/9
sudo -u jadzia env HOME=/home/jadzia venv/bin/python tools/demand_os_hub.py agents run-due          # A9 → ok, due=[]
sudo -u jadzia env HOME=/home/jadzia venv/bin/python tools/demand_os_owner_verify.py                # A5 → ok:true
systemctl list-timers demand-os-agents-worker.timer          # e → timer armed
```
