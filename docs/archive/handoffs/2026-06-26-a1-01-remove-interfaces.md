## Handoff: A1-01 — Usunięcie legacy `interfaces/`

**Data:** 2026-06-26
**Autor:** Agent

### Co zrobiono

- Zweryfikowano, że katalog `interfaces/` nie istnieje w drzewie źródłowym.
- Brak importów `from interfaces` / `import interfaces` w kodzie Python (`.py`, CI).
- Testy: **304 passed, 1 skipped, 1 xfailed** (baseline po usunięciu warstwy legacy).
- Pokrycie API: `tests/test_api_integration.py` (25 testów) + istniejące testy worker/health/webhooks.
- Zaktualizowano dokumentację operacyjną:
  - `CLAUDE.md` — flow i key files wskazują na `api/` + `core/agent.py`
  - `.agents/workflows/debug.md` — Layer 1 bez `interfaces/`
- `todo.json`: A1-01 → `completed`
- `jadzia.egg-info/SOURCES.txt` — regeneracja przez `pip install -e .`

### Weryfikacja parity

| Stary (`interfaces/`) | Nowy (`api/`) |
|------------------------|---------------|
| `interfaces/api.py` | `api/app.py` + `api/routes/*` |
| `interfaces/telegram_api.py` | `api/telegram.py` |
| `interfaces/telegram_worker_client.py` | `api/telegram_client.py` |
| `interfaces/webhooks.py` | `api/webhooks.py` |
| `interfaces/gemini_client.py` | `api/gemini.py` |

`main.py` używa `api.app.create_app()` — jedyny punkt wejścia FastAPI.

### Stan

- **A1-01**: completed
- **Testy**: zielone (304 passed)
- **Blokery**: brak

### Następny krok

**A4-01** (decyzja single persistence: SQLite-only vs dual JSON+SQLite) — wymaga `/blueprint` przed implementacją.

Alternatywa równoległa: dokończyć **A3-01** (pełna migracja logiki z `agent/agent.py` do `core/agent.py` — częściowo już zrobione).

**S1-01** (rotacja sekretów) — nadal blocked, wymaga Dowódcy.
