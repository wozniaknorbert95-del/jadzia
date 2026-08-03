# MASTER TODO 8 — Iteracja 3: weryfikacja 7-ki + hardening kontraktów (agents tool 100%)

**Status:** 🔵 ACTIVE (sesja 2026-08-03, trzecia iteracja cyklu)
**Kierunek:** tool-only; live marketing PARKED (hard lock `.cursor/rules/demand-os-tool-first.mdc`)
**Tip wejścia:** `1981ad4` (prod owner-verify ok:true)

## Definicja sesji (cykl jak w 6/7)

1. **Zaczynamy od weryfikacji poprzedniej 10-ki** (MASTER-TODO-7) na VPS i lokalnie — nie od ficzerów.
2. Defekty → rejestr → fixy z testami regresyjnymi.
3. Reszta = hardening kontraktów, które w 7-ce naprawiano ad-hoc (writable paths, sanitized pack, SoT tip) — mechanizujemy, żeby nie wracały.
4. Koniec = ship (commit + deploy + VPS verify + raport).

## Rejestr defektów 8-01 (weryfikacja 7-ki na VPS — pierwsza pełna suita na prod)

| ID | Defekt | Fix |
|----|--------|-----|
| D8-01 | Pełna `tests/unit` na VPS: **67 failed** — testy dziedziczyły prod `.env` (JWT_SECRET, JADZIA_ENV=production, webhooks, marketing HITL) przez `load_dotenv()` przy imporcie (5 modułów) | hermetic contract: `tests/conftest.py` stubuje `dotenv.load_dotenv` + flaga `JADZIA_TEST_NO_DOTENV` w `core/services.py` |
| D8-02 | VPS venv bez dev deps (`pytest-asyncio`, `pytest-cov`) — async testy i K12 coverage padały | zainstalowane w venv (deklaracja: `pyproject [project.optional-dependencies].dev`) |
| D8-03 | `test_flow_apply_emits_a2a_handoff`: VPS `.env` ma `DEMAND_OS_MARKETING_HITL=GO` → `publish_allowed=True` | test pinuje PARKED (`delenv`) — gate niezależny od hosta |
| D8-04 | `test_writable_set_now_default` zakładał writable checkout (na prod read-only) | test akceptuje set-now XOR fallback (oba poprawne wg kontraktu) |
| D8-05 | Deploy merge abort: pliki/katalogi root-owned w `/opt/jadzia` (wcześniejsze operacje jako root) + untracked 5F na VPS | `chown -R jadzia:jadzia` (0 root-owned) + dupes SAME usunięte; deploy playbook nota |

**Wynik 8-01:** VPS `688 passed, 0 failed, 21 skipped` · lokalnie `693 passed, 0 failed, 16 skipped`
(Δ5 = uczciwe env-skipy: flexgrafik-inspire sibling/vehicle template nieobecne na VPS — `skipif` by design).

## Backlog (10)

| ID | Zadanie | Status | DoD / Dowód |
|----|---------|--------|-------------|
| **8-01** | Weryfikacja 7-ki na VPS: pełna `tests/unit` na prod venv (nie tylko `-k demand_os`) + spot dogfood agents (dispatch read-action, flow dry, heartbeat read) na prod paths | ✅ | rejestr D8-01..05 wyżej; commity `234d57a`,`c60ce52`; VPS HEAD=`c60ce52` |
| **8-02** | Working-tree hygiene: każdy modified/untracked klasyfikowany — handoffy 08-01/08-03 → commit; `set-now` runtime modified lokalnie → świadoma decyzja per plik (checkout vs snapshot); `.superpowers`, `assets/`, `logs/` → zostaje z notą | ✅ | 5F data-commit `3dc7164`; runtime drift (6 plików) discarded; BLOG-DRAFTS/cal/events dogfood artifacts usunięte; k12 artifact zostaje do 8-07 |
| **8-03** | GDrive connector tool-side: real client za `list_cf_assets_stub`, fail-closed jak `ga4_adapter` (brak creds → `unavailable`, zero network w CI) + testy obu ścieżek | ✅ | `gdrive_cf.list_drive_folder` (SA+httpx, injectable transport, live gated `DEMAND_OS_GDRIVE_LIVE`) + `test_gdrive_cf_live.py` 7 testów; coverage doc sync |
| **8-04** | Worker loop per rola — **design doc przed kodem**: model (systemd timers per rola jak K13 ledger-export vs in-process), RBAC, idempotencja, live-gate, `shell:false` criteria | ✅ | design `AGENTS-WORKER-LOOP-DESIGN.md` (1 timer + due-dispatcher) + `agents/worker.py` + `run-due` (hub/CLI) + RBAC `agents-run-due` + `.service`/`.timer` + `test_agents_worker.py` 6/6 |
| **8-05** | Heartbeat staleness → doctor check: warn/FAIL gdy rola z cadence ma heartbeat >72h lub brak (przygotowanie pod worker loop; dziś manual dispatch) | ✅ | realizacja w wave-check (doctor dla agentów): `heartbeat_staleness` we wszystkich falach · limit 2×CADENCE (sales 12h, reszta 48h) + env override · 3 testy + dogfood red/green |
| **8-06** | Wave-check writable suite: W4 (lub nowy blok `state_writable`) mechanicznie sprawdza wszystkie writery: LEDGER, VALIDATOR-LOG, CONTROL-AUDIT, ENGAGE-LOG, BLOG-DRAFTS, GROWTH-EVENTS, A2A-HANDOFFS, AGENTS-HEARTBEAT, MEMORY, CONTENT-CALENDAR — resolvable + writable | ✅ | `state_writers_resolvable` w W1: 9/9 writerów z real write-probe · `memory.py`+`heartbeat.py` zmigrowane na `state_paths` (jedna ścieżka kontraktu) · 2 testy |
| **8-07** | Coverage gate: `tools/demand_os_coverage_check.py` — agents modules ≥80% line, exit 1 gdy poniżej; podpięty jako opcjonalny krok owner-verify (`--with-coverage`) + OWNER-VERIFY-COMMANDS.md | ✅ | realizacja jako test-gate (jak K12): `test_agents_coverage_gate.py` — w suite, więc owner-verify odpala z automatu · wyniki: registry 93.6 / flow 90.8 / wave_check 97.8 / heartbeat 92.5 / worker 94.7 / wave1 88.3 · evidence `k12-coverage-agents.{json,txt}` |
| **8-08** | Desk tile Agenci: staleness chip — `bieg: Nd` z progiem koloru (<24h ok / <72h warn / ≥72h lub nigdy stale) + cache bump `desk-dash13` + test kontraktu desk | ✅ | chip `dziś/Nd/nigdy` fresh≤2d / aging≤7d / stale + `age_days` w payload + `desk-dash13` + fixtures + 64 testy desk green |
| **8-09** | SoT tip check: owner-verify pointer-test porównuje `STATE.md prod_tip` z `git rev-parse --short HEAD` (po deploy = równe; przed = warn) — koniec ręcznego sync jak w 7-ce | ✅ | `test_sot_tip_pointer.py`: tip ∈ {HEAD, HEAD~1} (tip-sync commit tolerowany) · skip na dirty tree, untracked nie blokuje |
| **8-10** | Ship: pełny verify lokalny (unit + owner-verify), handoff 8, commit, deploy, VPS owner-verify, raport do Dowódcy | ✅ | unit **714/0** · root **336/0** · handoff `2026-08-03-DEMAND-OS-AGENTS-8-WORKER-HARDENING.md` · VPS verify w handoffie |

## Zakaz w tej sesji (niezmienny)

Live publish · Ads · `shell:false` bez worker loop · GA4 live bez GO · fake ledger rows ·
pchanie Dowódcy do unlock.

## Notatki z wejścia

- 7-ka deploy-time findings (`415306b` a2a, `ca922ff` engage, `1981ad4` pack parity) →
  motywacja dla 8-06/8-09: mechanizacja zamiast ad-hoc.
- GA4 live + social connectors live = PARKED (human credentials / unlock) — nie w backlogu.
