## Handoff: Fix state.py → package test failures

**Data:** 2026-06-02
**Autor:** Agent (sesja naprawcza po A2-01)

### Co się stało

Refaktor `agent/state.py` → `agent/state/` pakiet wykonany, ale testy nie przechodziły (32 failed).

### Przyczyny (3 błędy)

1. **`agent/state/locks.py:36`** — `agent_lock` zdefiniowany jako `def` zamiast `@contextmanager def`, przez co generator nie działał jako context manager → `TypeError: 'generator' object does not support the context manager protocol`
2. **`agent/state/tasks.py:215`** i **`agent/state/_helpers.py:66-67`** — brak `import time`, mimo że kod woła `time.time()` → `NameError: name 'time' is not defined`
3. **`agent/state/__init__.py:2`** — nie exportował `_check_invariants` (prywatna funkcja używana przez `test_reliability_regression.py`)

### Naprawione

- `locks.py`: dodano `@contextmanager` przed `def agent_lock`
- `tasks.py`, `_helpers.py`: dodano `import time`
- `__init__.py`: dodano `_check_invariants` do re-exportów

### Stan

- **59 passed, 1 xfailed** (wszystkie testy przechodzą)
- **A2-01**: wykonane, stan `completed`
- **`agent/state.py`**: usunięty, zastąpiony przez `agent/state/` (6 plików)

### Blokery / Ryzyka

- Brak znanych. Wszystkie importy i funkcje backward-compat sprawdzone.
- Zalecane: przed kolejnym refaktorem (np. A1-01: usunięcie `interfaces/`) uruchomić najpierw testy, żeby mieć baseline.
