# Handoff: Refactor — modularizacja kodu

**Data**: 2026-06-01
**Agent**: opencode (deepseek-v4-flash-free)
**Stan**: DONE

## Co zrobiono

Zrefaktorowano monolityczny kod do nowej, modułowej struktury zgodnie z `docs/opencode-prompts/refactor-modularization.md`.

### Nowa struktura pakietów

```
jadzia-core/
├── core/                       # Logika domenowa i modele
│   ├── __init__.py
│   ├── models.py               # Wszystkie modele Pydantic (100% test coverage)
│   └── services.py             # Abstrakcje serwisów + implementacje (79% coverage)
│
├── api/                        # Warstwa FastAPI
│   ├── __init__.py
│   ├── app.py                  # Fabryka FastAPI (create_app) + worker loop
│   ├── _state.py               # Współdzielony stan: _worker_loop_ref, health_metrics
│   ├── dependencies.py         # FastAPI Depends dla DI (Claude, Gemini, WooCommerce serwisy)
│   ├── gemini.py               # Wrapper Gemini research
│   ├── telegram.py             # Re-export z interfaces.telegram_api
│   ├── telegram_client.py      # Re-export z interfaces.telegram_worker_client
│   ├── webhooks.py             # Re-export z interfaces.webhooks
│   └── routes/
│       ├── chat.py             # /chat, /api/v1/widget/chat
│       ├── health.py           # /, /health, /status, /rollback, /test-ssh, /clear
│       ├── worker.py           # /worker/task, /worker/task/{id}/input, /tasks/cleanup
│       ├── dashboard.py        # /worker/dashboard, /worker/health
│       ├── costs.py            # /costs, /costs/reset, /costs/estimate
│       └── sessions.py         # /sessions, /sessions/cleanup
│
├── cli/                        # CLI (szkielet)
│   └── __init__.py
│
├── tests/unit/                 # Nowe testy jednostkowe (82 testy)
│   ├── conftest.py
│   ├── test_models.py          # 100% core.models
│   ├── test_services.py        # ~79% core.services
│   ├── test_dependencies.py    # DI wiring + JWT auth
│   ├── test_api_state.py       # api._state
│   ├── test_api_init.py        # api/ struktura
│   ├── test_core_init.py       # core/ struktura
│   └── test_cli.py             # cli/ szkielet
```

### Kluczowe zmiany

1. **core/models.py** — skonsolidowane wszystkie modele Pydantic: Chat, Worker Task, Telegram, Health, Dashboard, Cost, Operation State (177 linii, 100% coverage).

2. **core/services.py** — abstrakcyjne interfejsy serwisów z implementacjami:
   - `ClaudeService` / `AnthropicClaudeService` — LLM (z model selection, cost tracking)
   - `GeminiService` / `DefaultGeminiService` — research (SDK google-generativeai)
   - `WooCommerceService` / `SshWooCommerceService` — shop (SSH + HTTP)
   - `NotificationService` / `DiscordNotificationService` — alerty
   - `ServiceRegistry` — rejestr do DI, singleton z `get_registry()/set_registry()/reset_registry()`

3. **api/dependencies.py** — FastAPI `Depends` dla wstrzykiwania serwisów + `verify_jwt` auth dependency.

4. **api/app.py** — fabryka `create_app()` z rejestracją routerów, CORS, startup/shutdown (worker loop).

5. **main.py** — używa `api.app.create_app()` zamiast `interfaces.api.app`.

6. **pyproject.toml** — dodano `filelock>=3.0.0` do zależności, `google-generativeai` jako optional, `pytest-cov` do dev, rozszerzono `packages.find`.

### Zachowana kompatybilność wsteczna

- Stare pakiety `agent/` i `interfaces/` pozostają nietknięte
- Nowe `api/` route'y delegują logikę do istniejących modułów `agent.*`
- `api/telegram.py`, `api/telegram_client.py`, `api/webhooks.py` to re-exporty z `interfaces.*`

## Wyniki walidacji

- **ruff check**: All checks passed
- **pytest tests/unit/**: 82 passed, 0 failed
- **Coverage core/**: ~87% (models 100%, services 79%)
- **Coverage api/**: niższa (route'y wymagają testów integracyjnych z FastAPI TestClient)

## Zalecenia na przyszłość

1. Dopisać testy integracyjne dla `api/app.py` i route'ów (użycie `TestClient`)
2. Stopniowo przenosić logikę z `agent/*` do `core/*` (docelowo `core/` ma być samowystarczalne)
3. Przenieść `SshWooCommerceService` do pełnej implementacji bez delegacji do `agent.tools`
4. Dodać testy integracyjne dla worker loop (`_worker_loop`)
5. Rozważyć dodanie `ruff` i `mypy` do CI
