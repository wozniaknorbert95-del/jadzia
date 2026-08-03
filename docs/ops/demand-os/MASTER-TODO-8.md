# MASTER TODO 8 — Iteracja 3: weryfikacja 7-ki + hardening kontraktów (agents tool 100%)

**Status:** 🔵 ACTIVE (sesja 2026-08-03, trzecia iteracja cyklu)
**Kierunek:** tool-only; live marketing PARKED (hard lock `.cursor/rules/demand-os-tool-first.mdc`)
**Tip wejścia:** `1981ad4` (prod owner-verify ok:true)

## Definicja sesji (cykl jak w 6/7)

1. **Zaczynamy od weryfikacji poprzedniej 10-ki** (MASTER-TODO-7) na VPS i lokalnie — nie od ficzerów.
2. Defekty → rejestr → fixy z testami regresyjnymi.
3. Reszta = hardening kontraktów, które w 7-ce naprawiano ad-hoc (writable paths, sanitized pack, SoT tip) — mechanizujemy, żeby nie wracały.
4. Koniec = ship (commit + deploy + VPS verify + raport).

## Backlog (10)

| ID | Zadanie | Status | DoD / Dowód |
|----|---------|--------|-------------|
| **8-01** | Weryfikacja 7-ki na VPS: pełna `tests/unit` na prod venv (nie tylko `-k demand_os`) + spot dogfood agents (dispatch read-action, flow dry, heartbeat read) na prod paths | open | rejestr defektów D1′–Dn′ (może być pusty = PASS) |
| **8-02** | Working-tree hygiene: każdy modified/untracked klasyfikowany — handoffy 08-01/08-03 → commit; `set-now` runtime modified lokalnie → świadoma decyzja per plik (checkout vs snapshot); `.superpowers`, `assets/`, `logs/` → zostaje z notą | open | `git status` → każda pozycja rozliczona w handoffie |
| **8-03** | GDrive connector tool-side: real client za `list_cf_assets_stub`, fail-closed jak `ga4_adapter` (brak creds → `unavailable`, zero network w CI) + testy obu ścieżek | open | moduł + testy; desk `gdrive_local_registry` check bez zmian (stub fallback) |
| **8-04** | Worker loop per rola — **design doc przed kodem**: model (systemd timers per rola jak K13 ledger-export vs in-process), RBAC, idempotencja, live-gate, `shell:false` criteria | open | `docs/ops/demand-os/AGENTS-WORKER-LOOP-DESIGN.md` + decyzja; implementacja tylko jeśli design ≤1 timer |
| **8-05** | Heartbeat staleness → doctor check: warn/FAIL gdy rola z cadence ma heartbeat >72h lub brak (przygotowanie pod worker loop; dziś manual dispatch) | open | check w `doctor.py` + test (fresh=ok, stale=warn, none=warn) |
| **8-06** | Wave-check writable suite: W4 (lub nowy blok `state_writable`) mechanicznie sprawdza wszystkie writery: LEDGER, VALIDATOR-LOG, CONTROL-AUDIT, ENGAGE-LOG, BLOG-DRAFTS, GROWTH-EVENTS, A2A-HANDOFFS, AGENTS-HEARTBEAT, MEMORY, CONTENT-CALENDAR — resolvable + writable | open | checki w `wave_check.py` + test (tmp writable vs read-only → fallback path) |
| **8-07** | Coverage gate: `tools/demand_os_coverage_check.py` — agents modules ≥80% line, exit 1 gdy poniżej; podpięty jako opcjonalny krok owner-verify (`--with-coverage`) + OWNER-VERIFY-COMMANDS.md | open | skrypt + dok; K12 artifacts regenerowane |
| **8-08** | Desk tile Agenci: staleness chip — `bieg: Nd` z progiem koloru (<24h ok / <72h warn / ≥72h lub nigdy stale) + cache bump `desk-dash13` + test kontraktu desk | open | UI + test `test_demand_desk_ui_contracts` rozszerzony |
| **8-09** | SoT tip check: owner-verify pointer-test porównuje `STATE.md prod_tip` z `git rev-parse --short HEAD` (po deploy = równe; przed = warn) — koniec ręcznego sync jak w 7-ce | open | check w owner-verify + test |
| **8-10** | Ship: pełny verify lokalny (unit + owner-verify), handoff 8, commit, deploy, VPS owner-verify, raport do Dowódcy | open | `ok:true` na VPS @ nowy tip |

## Zakaz w tej sesji (niezmienny)

Live publish · Ads · `shell:false` bez worker loop · GA4 live bez GO · fake ledger rows ·
pchanie Dowódcy do unlock.

## Notatki z wejścia

- 7-ka deploy-time findings (`415306b` a2a, `ca922ff` engage, `1981ad4` pack parity) →
  motywacja dla 8-06/8-09: mechanizacja zamiast ad-hoc.
- GA4 live + social connectors live = PARKED (human credentials / unlock) — nie w backlogu.
