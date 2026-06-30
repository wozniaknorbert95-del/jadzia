## Handoff: C1-04 — Testy integracyjne API

**Data:** 2026-06-02
**Autor:** Agent

### Co zrobiono

Nowy plik `tests/test_api_integration.py` — 25 testów dla `api/app.py` (create_app).

### Coverage

| Kategoria | Testy | Opis |
|-----------|-------|------|
| Route registration | 2 | Wszystkie 20 tras zarejestrowane, Telegram nie załadowany bez ENV |
| Health endpoints | 8 | Root, health, status idle/active, logs, clear, rollback, test-ssh |
| Worker endpoints | 6 | Create, get found/not-found, locked, worker health, dashboard no-SQLite |
| Session endpoints | 2 | List, cleanup |
| Cost endpoints | 1 | Estimate (tiktoken mockowany przez sys.modules) |
| JWT auth | 3 | 401 bez tokena, 200 z tokenem, 401 z invalid token |
| Error handling | 3 | 404, 422, 500 |

### Kluczowe decyzje techniczne

- `create_app()` bez context managera → startup events nie fire'ują się (worker loop nie startuje)
- Mocki przez `patch("agent.state.*")` lub `patch("agent.tools.rest.*")` — bo health.py używa lokalnych importów wewnątrz funkcji
- Worker routes mockowane przez `api.routes.worker.*` — bo importują `from agent.state import ...` na poziomie modułu
- tiktoken nieobecny w środowisku → mock przez `patch.dict("sys.modules", {"tiktoken": mock})`
- Test 500 używa `raise_server_exceptions=False`

### Stan

- **255 passed, 2 failed (pre-existing), 1 xfailed**
- **C1-04**: `completed` w todo.json
- **A2-01**: status zmieniony na `completed`

### Co dalej

Najsensowniejszy następny krok: **A1-01 (usunięcie legacy interfaces/)** — mamy już testy na `api/app.py`, więc można śmiało zweryfikować parity i wywalić stary kod. Albo **A4-01 (single persistence decision)**.

2 pre-existing failing tests (niezależne od zmian):
- `test_customer_chat_caching` — assert 4 == 3
- `test_route_approval` — routing logic issue
