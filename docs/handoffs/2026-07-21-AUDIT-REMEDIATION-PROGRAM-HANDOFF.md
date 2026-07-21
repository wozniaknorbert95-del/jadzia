# Handoff — Jadzia Core Audit Remediation Program

**Date:** 2026-07-21  
**Parent task:** `AUD-REM-00`  
**Audit baseline:** local `master` @ `29043cb76aea934ab74d263655383f0787876311`  
**Program status:** READY · implementation not started  
**Production:** UNVERIFIED · no deploy · `standing_go_closeout=false`

## Decision

Uruchomić pełny program remediacji wszystkich findings z
`docs/ops/JADZIA-CORE-AUDIT-2026-07-21.md`. Praca jest sekwencyjna:
jedna sesja = jeden task = jeden moduł = jeden handoff. Nie robimy mega-diffu.

Pierwszym zadaniem jest `AUD-REM-CI-01`, ponieważ obecny CI daje zielony wynik
14/14 przy pełnym suite z 6 błędami. Dopóki pełny gate nie jest wiarygodny,
nie można uczciwie potwierdzać kolejnych poprawek.

## Operating model — standard agencyjny

Każdy task przechodzi ten sam łańcuch:

1. `@vibe-init` — odczyt SoT, dirty state, klasyfikacja i invariants.
2. Właściwy workflow:
   - regresja/test: `@debug`
   - refactor/runtime: `@blueprint`
   - dependency: `@dep-audit`
   - implementacja: `@implement`
3. Testy modułowe + pełny wymagany gate `@jadzia-test`.
4. Security-sensitive diff: `@audit-red-team`.
5. Handoff z dowodami, bez fake PASS.
6. Commit/PR tylko na jawne polecenie. VPS/deploy tylko po świeżym GO.

Każdy finding ma zamknięcie oparte na dowodzie: kod + test negatywny + test
regresyjny + aktualizacja dokumentacji kontraktowej. Sam opis lub mock bez
negatywnego scenariusza nie zamyka findingu.

## Program sekwencyjny

### Wave 1 — odzyskanie zaufania do wydania

1. `AUD-REM-CI-01` — naprawić/rozstrzygnąć 6 błędów pełnego suite; uruchamiać
   pełny blocking pytest i generować prawdziwy `coverage.xml`.
2. `AUD-REM-QUALITY-01` — urealnić Ruff/Black/Mypy baseline, naprawić martwy
   `tests/integration`, dodać route coverage i minimalny Commander UI smoke.

**Gate W1:** pełny wymagany pytest zielony; CI nie może przejść przy regresji
poza design-agent; workflow testowy odpowiada rzeczywistym komendom.

### Wave 2 — granice zaufania i supply chain

3. `AUD-REM-CALLBACK-01` — zamknąć SSRF callbacku: allowlist/registry,
   blokada private/link-local i redirectów, limity, redakcja logów.
4. `AUD-REM-SSH-01` — known-host pinning, `RejectPolicy`, usunięcie
   niebezpiecznego shell interpolation i bezpieczne rozpakowanie tar.
5. `AUD-REM-DEPS-01` — pełny lock na czystym Python 3.11, Chroma mitigation,
   blocking `pip-audit` i secret scan w CI.
6. `AUD-REM-INGRESS-01` — rate limits i payload limits, server-issued widget
   session IDs, Telegram secret także dla native update, trwały dedup,
   Brain Bus idempotency i świadoma polityka OpenAPI/status/health.

**Gate W2:** negatywne testy SSRF/MITM/replay/rate-limit przechodzą; zero
high/critical dependency advisory bez udokumentowanej kompensacji.

### Wave 3 — integralność wykonania i obserwowalność

7. `AUD-REM-WRITE-01` — all-or-rollback dla wieloplikowych zapisów,
   poprawne statusy i konfigurowalny health target.
8. `AUD-REM-HEALTH-01` — jeden metrics store, forced-failure E2E,
   correlation `task_id/chat_id`, trwałość lub jawny kontrakt cost metrics.
9. `AUD-REM-DB-01` — contention benchmark, WAL/busy timeout po pomiarze,
   source-aware lock key, single-process invariant i idempotent scheduler.

**Gate W3:** fault-injection nie pozostawia partial success; health pokazuje
realny błąd; DB benchmark ma zapisany próg i wynik.

### Wave 4 — prywatność, operacje i recovery

10. `AUD-REM-PRIVACY-01` — retention cleanup/anonymization, data minimization
    Telegram/logów i test izolacji/TTL sesji widget.
11. `AUD-REM-OPS-01` — SLO/error budget, RPO/RTO, off-site backup policy,
    restore drill, systemd hardening i bezpieczny deploy bez domyślnego uploadu DB.
12. `AUD-REM-SOT-01` — jeden current prod tip, definicje readiness, rolling
    OPS-AI re-window procedure, działające linki i ≤15 aktywnych handoffów.

**Gate W4:** retention ma wykonany test; restore ma evidence; docs nie zgłaszają
sprzecznych tipów ani nieaktualnego PASS.

### Wave 5 — niezależne potwierdzenie produkcji

13. `AUD-REM-VPS-VERIFY-01` — dopiero po świeżym GO: read-only evidence VPS,
    następnie kontrolowany deploy przez Dowódcę i post-deploy smoke, jeśli
    osobny task wdrożeniowy uzyska GO.

**Gate końcowy:** niezależny re-audit zamyka każde F-01–F-13 jako PASS albo
pozostawia jawny residual risk. Bez dowodu runtime produkcja pozostaje UNVERIFIED.

## Critical warnings

- Nie dotykać istniejących zmian:
  `.cursor/session-state.md`, `deployment/mkt-dash01-verify.sh`,
  `docs/handoffs/2026-07-19-SESSION-CLOSE-MKT-DASH.md`.
- Nie łączyć CI + SSRF + SSH + DB w jednym PR.
- Nie formatować mechanicznie 165 plików w tasku CI; quality baseline ma osobny task.
- Nie uruchamiać VPS, Meta, Mollie, FB, GA4 ani płatnych LLM bez właściwego gate/GO.
- Nie oznaczać audytu produkcyjnego PASS na podstawie handoffu lub lokalnego testu.
- Human parks Marketing OS pozostają zamrożone i nie są długiem tego programu.

## Exact next session

**Task:** `AUD-REM-CI-01`  
**Classification:** BUGFIX / release engineering  
**Workflow:** `@vibe-init` → `@debug` → `@implement` → `@jadzia-test` → `@handoff`  
**Scope:** tylko pełny pytest, sześć bieżących regresji, CI coverage artifact i
blocking gate. Bez Ruff mega-format, SSRF, SSH, dependencies i VPS.

### Definition of Done

- `pytest tests/` kończy się bez failed.
- Każdy z sześciu błędów ma RCA: bug w kodzie albo stale test-contract.
- Oba obecne workflow CI są scalone albo mają jednoznaczny blocking ownership.
- CI uruchamia uzgodniony pełny suite i generuje istniejący `coverage.xml`.
- Negatywny test dowodzi, że regresja poza design-agent blokuje workflow.
- Handoff zapisuje czas gate, wynik i listę świadomie odroczonych quality errors.

## V-FILES

1. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\ops\JADZIA-CORE-AUDIT-2026-07-21.md`
2. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\handoffs\2026-07-21-AUDIT-REMEDIATION-PROGRAM-HANDOFF.md`
3. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\todo.json`
4. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\.github\workflows\ci.yml`

## Start prompt for the new session

```text
@vibe-init

TASK_ID: AUD-REM-CI-01

Jesteś lead engineerem programu Jadzia Core Audit Remediation. Pracuj jak
senior release engineering team: evidence-first, zero fake PASS, jedna sesja =
jedno zadanie = jeden moduł.

Najpierw przeczytaj:
1. docs/handoffs/2026-07-21-AUDIT-REMEDIATION-PROGRAM-HANDOFF.md
2. docs/ops/JADZIA-CORE-AUDIT-2026-07-21.md
3. todo.json — AUD-REM-00 i AUD-REM-CI-01
4. .github/workflows/ci.yml oraz .github/workflows/tests.yml

Wykonaj wyłącznie AUD-REM-CI-01:
- uruchom /debug dla 6 błędów pełnego pytest,
- rozdziel bug kodu od stale test-contract,
- doprowadź pytest tests/ do 0 failed,
- napraw blocking CI i realny coverage.xml,
- nie rób globalnego Ruff/Black/Mypy cleanup,
- nie dotykaj SSRF, SSH, DB, dependencies ani VPS.

Potem uruchom @jadzia-test w zakresie taska, zapisz evidence i zakończ @handoff.
Nie commituj i nie deployuj bez jawnego polecenia.
```
