---
status: COMPLETED
archived: 2026-06-30
---

# Plan Remediacji — jadzia-core

**Status:** COMPLETED (archived 2026-06-26)  
**Successor:** [`PLAN-COI-PHASE-A.md`](PLAN-COI-PHASE-A.md)

**Data**: 2026-06-02
**Źródło**: `docs/audyt-raport.txt` (25 findings) + `docs/plans/STAGE2-JADZIA-DONE.md`
**Status workflow**: v2.0 Elite Edition wdrożony (L0-L4)
**Autor**: Senior Team Specialist

---

## Krótki raport stanu

Audyt zidentyfikował **25 znalezisk** (2 krytyczne, 23 średnie/niskie).  
Część workflowowych (W1) została **już zaadresowana** w tej sesji poprzez podmianę na v2.0 Elite Edition:
- `/implement` — istnieje
- `Refactor` — `/blueprint` dodany
- F1-F5 → L0-L4 — ujednolicone
- V-FILES — zdefiniowane w output formatach
- `handoff.md` — pełny template
- `pre-flight.md` — usunięty (routing L0 → L2)

Pozostałe **20 znalezisk** podzielono na 4 sprinty.

---

## Sprint 1 — Bezpieczeństwo (CRITICAL) — 1-2 dni

| ID | Audyt | Zadanie | Ryzyko | Trudność |
|----|-------|---------|--------|----------|
| S1-01 | S1 | **Rotacja sekretów**: nowe klucze API, SSH, Telegram; `git filter-branch`/BFG do usunięcia `.env` z historii | LIVE secrets w repo — najwyższe | Medium |
| S1-02 | S2 | **Ujednolicenie dependencji**: zsynchronizować `pyproject.toml` i `requirements.txt` wersje bibliotek | Działające CI ale "works on my machine" | Niska |
| S1-03 | S3 | **Dedicated system user**: `jadzia.service` → user `jadzia` (nie root) z ograniczonymi prawami | Root na VPS = pełna kontrola przy exploicie | Średnia |
| S1-04 | S4 | **Lockfile**: `pip freeze > requirements.lock` lub `poetry lock`, skomitować | Reprodukowalność buildów = 0 | Niska |

## Sprint 2 — Architektura — 3-5 dni

| ID | Audyt | Zadanie |
|----|-------|---------|
| A1-01 | A1 | **Usunięcie `interfaces/`**: zweryfikować że `api/` pokrywa wszystkie endpointy, usunąć stary kod, wyczyścić importy |
| A2-01 | A3 | **Podział `agent/state.py`**: `state/core.py`, `state/locks.py`, `state/migration.py`, `state/sync.py` |
| A3-01 | A4 | **Migracja logiki agenta**: przenieść `process_message` z `agent/agent.py` do `core/agent.py`, przepiąć worker loop |
| A4-01 | A2 | **Single persistence**: zdecydować — SQLite tylko (drop JSON fallback) lub zostawić dualny stan |
| A5-01 | A5 | **CLI**: zaimplementować entry point lub usunąć szkielet |

## Sprint 3 — CI/Developer Experience — 2-3 dni

| ID | Audyt | Zadanie |
|----|-------|---------|
| C1-01 | Q2 | **mypy w CI**: dodać `mypy --strict` do workflow |
| C1-02 | Q3 | **Konfiguracja ruff + black** w `pyproject.toml` (`[tool.ruff]`, `[tool.black]`) |
| C1-03 | Q4 | **pre-commit hooks**: `.pre-commit-config.yaml` z ruff, black, mypy |
| C1-04 | Q5 | **Testy integracyjne API**: `TestClient` dla `api/app.py` — smoke testy endpointów |
| C1-05 | W4 | **Artefakty deploy**: przenieść `.tar.gz`, `.ps1`, `.bat`, `ngrok.*`, `deploy_answers.txt`, `Project-Instructions.md` do `archive/` |

## Sprint 4 — Dokumentacja i porządki — 1-2 dni

| ID | Audyt | Zadanie |
|----|-------|---------|
| D1-01 | W2 | **Aktualizacja `brain.md`**: stage F1-F5 → L0-L4, lista workflow |
| D1-02 | W3 | **PRD-schema.md**: utworzyć lub poprawić referencję w `docs/PRD-core.md` |
| D1-03 | Q1 | **Standaryzacja języka**: cały kod i komentarze po EN |
| D1-04 | Q6 | **Utrzymanie `todo.json`**: aktualizować na bieżąco |

---

## Podsumowanie

| Sprint | Tasks | Effort | Dependencies |
|--------|-------|--------|-------------|
| S1 — Security | 4 | 1-2 dni | Żadne |
| S2 — Architektura | 5 | 3-5 dni | S1 done |
| S3 — CI/DevX | 5 | 2-3 dni | Żadne |
| S4 — Docs | 4 | 1-2 dni | S2 (brain.md po refactorze) |
| **Total** | **18** | **7-12 dni** | |

## Rekomendacja

**Zacząć od S1-01** (rotacja sekretów) — to jedyne krytyczne ryzyko.  
Równolegle można robić S1-02 i S1-04 (niskie, bezpieczne).  
S3 niezależny od S2 — można robić równolegle.  
S4 zależny od S2 (brain.md po refactorze).
