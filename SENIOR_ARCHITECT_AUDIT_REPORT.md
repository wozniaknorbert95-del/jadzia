# SENIOR ARCHITECT AUDIT – JADZIA

---

## 1. STRUKTURA PROJEKTU

Drzewo katalogów (główne foldery i pliki; bez pełnego venv):

```
projekty/Jadzia/
├── .cursor/
├── .github/
│   └── workflows/
├── agent/
│   ├── agent.py          # Główna logika agenta, process_message
│   ├── db.py             # SQLite – sesje, zadania
│   ├── state.py          # Stan sesji (SQLite/JSON)
│   ├── log.py            # Audit trail → logs/agent.log
│   ├── prompt.py
│   ├── telegram_formatter.py
│   ├── telegram_validator.py
│   ├── guardrails.py
│   ├── alerts.py
│   ├── diff.py
│   ├── helpers.py
│   ├── context/
│   │   ├── __init__.py
│   │   ├── smart_context.py
│   │   └── project_info.py
│   ├── nodes/
│   │   ├── __init__.py
│   │   ├── routing.py    # Routing wejścia użytkownika
│   │   ├── commands.py
│   │   ├── planning.py
│   │   ├── approval.py
│   │   ├── generate.py
│   │   ├── intent.py
│   │   └── quality.py
│   └── tools/
│       ├── __init__.py
│       ├── ssh_pure.py       # Czyste I/O SSH/SFTP
│       ├── ssh_orchestrator.py  # Zapis do hostingu (write_file, backup)
│       ├── rest.py
│       └── wp_explorer/
├── interfaces/
│   ├── api.py            # FastAPI, Worker API, worker loop
│   ├── telegram_api.py   # Handler komend Telegram (webhook)
│   ├── telegram_worker_client.py  # Klient Worker API (create_task, submit_input)
│   └── webhooks.py       # Powiadomienia webhook, health metrics
├── scripts/
│   ├── send_task.py
│   ├── jwt_token.py
│   ├── cleanup_db.py
│   ├── migrate_json_to_sqlite.py
│   └── ...
├── tests/
├── deployment/
├── docs/
├── data/                 # jadzia.db, sessions
├── logs/                 # agent.log (JSON Lines)
├── main.py               # Punkt wejścia (uvicorn)
├── requirements.txt
├── pyproject.toml
├── .env                  # Konfiguracja (sekrety)
└── verify_env.py
```

**Uwaga:** Brak `package.json` – projekt jest w 100% Python.

---

## 2. TECH STACK

| Element | Wartość |
|--------|---------|
| **Język** | Python 3.12 (wymagany >=3.11 w pyproject.toml) |
| **Framework Telegram** | Brak python-telegram-bot – webhook FastAPI + Telegram Bot API (httpx) do `sendMessage` |
| **Hosting motywu** | WordPress (ścieżka na serwerze: `BASE_PATH` = katalog public_html) |
| **Metoda połączenia z hostingiem** | **SSH/SFTP** (Paramiko) – `agent/tools/ssh_pure.py`, `agent/tools/ssh_orchestrator.py` |
| **Baza danych** | **SQLite** – `data/jadzia.db` (agent/db.py). Tabele: `sessions`, `tasks`. Stan sesji przy `USE_SQLITE_STATE=1`. |

---

## 3. GŁÓWNE PLIKI – PEŁNA ZAWARTOŚĆ

### 3.1 Plik startowy: `main.py`

```python
"""
main.py — Punkt wejścia aplikacji JADZIA

Uruchomienie:
    python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload

Lub:
    python main.py
"""

import os
import sys
from pathlib import Path

# Upewnij się że katalog projektu jest w PATH
PROJECT_DIR = Path(__file__).parent
sys.path.insert(0, str(PROJECT_DIR))

# Utwórz folder data jeśli nie istnieje
(PROJECT_DIR / "data").mkdir(exist_ok=True)

# Import aplikacji FastAPI
from interfaces.api import app

# Eksportuj app dla uvicorn
__all__ = ["app"]


def main():
    """Uruchom serwer bezpośrednio"""
    import uvicorn

    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", 8000))

    print("=" * 60)
    print("  JADZIA - AI Agent do zarządzania sklepem")
    print("=" * 60)
    print(f"  Uruchamiam na: http://{host}:{port}")
    print(f"  Dokumentacja:  http://{host}:{port}/docs")
    print("=" * 60)
    print()

    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True,
        reload_dirs=[str(PROJECT_DIR / "agent"), str(PROJECT_DIR / "interfaces")]
    )


if __name__ == "__main__":
    main()
```

### 3.2 Handler komend Telegram: `interfaces/telegram_api.py` (fragmenty kluczowe)

- **Endpoint:** `POST /telegram/webhook` (router z prefixem `/telegram`).
- **Wejście:** Telegram Update (native) lub n8n (body z `chat_id`, `user_id`, `message`, `callback_data`).
- **Parsowanie komend:** `parse_telegram_command(message, callback_data)` → `("zadanie"|"status"|"cofnij"|"pomoc"|"callback"|"approval"|"message", payload)`.
- **Obsługa:**
  - **zadanie** / **message** → `create_task(instruction, chat_id, jwt, base_url)` → Worker API `POST /worker/task` → Quick ACK do użytkownika; worker loop przetwarza w tle i push przez `send_awaiting_response_to_telegram`.
  - **callback** (Tak/Nie) → `parse_callback_approval` → `submit_input(task_id, jwt, base_url, approval=...)` → `POST /worker/task/{id}/input`.
  - **approval** (tak/nie) → `_get_task_id_for_chat(chat_id)` → `submit_input(...)`.
  - **status** → `get_task(task_id, jwt, base_url)` → odpowiedź ze statusem.
  - **cofnij** → `do_rollback(base_url)` → `POST /rollback`.
  - **pomoc** → `get_help_message()`.
- **Odpowiedzi do Telegrama:** Gdy `TELEGRAM_BOT_TOKEN` jest ustawiony – `_send_telegram_replies()` / `send_awaiting_response_to_telegram()` wywołują Telegram Bot API `sendMessage` (URL: `https://api.telegram.org/bot{token}/sendMessage`).
- **Idempotentność:** Deduplikacja po `update_id` (TTL 300 s) w `_is_duplicate_update`.

*(Pełny plik ma ~420 linii – powyżej opisana jest logika; kod już został wczytany w audycie.)*

### 3.3 Moduł zapisujący do motywu/hostingu: `agent/tools/ssh_orchestrator.py` (fragmenty)

- **Konfiguracja z .env:** `SSH_HOST`, `SSH_PORT`, `SSH_USER`, `SSH_PASSWORD`, `SSH_KEY_PATH`, `BASE_PATH` (oraz legacy `CYBERFOLKS_*`).
- **Funkcje eksportowane:** `read_file(path)`, `write_file(path, content, operation_id=..., chat_id=..., source=..., task_id=...)`, `list_directory`, `list_files`, `exec_ssh_command`, `get_path_type`, `file_exists`, `directory_exists`.
- **Zapis pliku:** `write_file()` – walidacja `validate_operation(WRITE)`, `validate_content`, dla `.php` – `check_wordpress_safety`; backup `{path}.backup.{timestamp}` przez SFTP; `write_file_ssh`; `mark_file_written(path, backup_path, chat_id, source, task_id)` w state.
- **SSH I/O:** Delegacja do `agent/tools/ssh_pure.py` (`read_file_ssh`, `write_file_ssh`, `write_file_ssh_bytes`, `list_directory_ssh`, `exec_command_ssh`, `get_path_type_ssh`), z retry (`@with_retry`).

*(Pełny plik ~260 linii – powyżej opisana jest rola i flow zapisu.)*

### 3.4 Konfiguracja (bez sekretów – wartości zastąpione przez XXX)

Struktura `.env` (wszystkie wartości jako XXX):

```env
# Claude API (Anthropic)
ANTHROPIC_API_KEY=XXX

# SSH
SSH_HOST=XXX
SSH_PORT=XXX
SSH_USER=XXX
SSH_KEY_PATH=XXX
BASE_PATH=XXX
SHOP_URL=XXX
LOCAL_REPO_PATH=XXX

# API
API_HOST=XXX
API_PORT=XXX

# Telegram (webhook, whitelist)
TELEGRAM_WEBHOOK_SECRET=XXX
ALLOWED_TELEGRAM_USERS=XXX

# Opcjonalne (nie w .env w repo – do uzupełnienia na VPS):
# TELEGRAM_BOT_TOKEN=XXX        # Wymagany do wysyłania odpowiedzi w Telegramie
# TELEGRAM_BOT_ENABLED=1        # Włącza router /telegram w FastAPI
# JWT_SECRET=XXX                # Do weryfikacji Worker API i generowania JWT
# TELEGRAM_BOT_JWT_TOKEN=XXX    # Alternatywa do JWT_SECRET dla bota
# TELEGRAM_BOT_API_BASE_URL=XXX # Domyślnie http://127.0.0.1:8000

# Legacy (compat)
CYBERFOLKS_HOST=XXX
CYBERFOLKS_PORT=XXX
CYBERFOLKS_USER=XXX
CYBERFOLKS_KEY_PATH=XXX
CYBERFOLKS_BASE_PATH=XXX

# Stan
USE_SQLITE_STATE=1
```

---

## 4. FLOW KOMENDY (przykład: `/zadanie zmień kolor przycisku`)

1. **User wysyła w Telegramie:** `/zadanie zmień kolor przycisku` (lub w grupie: `/zadanie@JadziaBot zmień kolor przycisku`).

2. **Bot odbiera przez:** Telegram wysyła Update na webhook → `POST /telegram/webhook` → `telegram_webhook()` w `interfaces/telegram_api.py` → parsowanie body jako Telegram Update → `normalize_telegram_update(body)` → `_handle_webhook_request(normalized, ..., skip_webhook_secret=True)`.

3. **Przetwarza przez:**
   - `parse_telegram_command(message, callback_data)` → `("zadanie", "zmień kolor przycisku")`.
   - `get_jadzia_chat_id(request.user_id)` → `chat_id = "telegram_6746343970"`.
   - `get_bot_jwt_token()` (z `TELEGRAM_BOT_JWT_TOKEN` lub `JWT_SECRET`).
   - `create_task("zmień kolor przycisku", chat_id, jwt, base_url)` w `telegram_worker_client` → **POST** `{base_url}/worker/task` z `instruction`, `chat_id`, `test_mode`.
   - W `interfaces/api.py`: `worker_create_task` → `add_task_to_queue(chat_id, task_id, instruction, "telegram", ...)` → zapis do SQLite (sessions/tasks) → **odpowiedź 200** z `task_id`, `position_in_queue`.
   - Webhook zwraca Quick ACK i wywołuje `_send_telegram_replies()` z komunikatem typu „Przyjęto zadanie (pozycja w kolejce: 1)…”.

4. **Zapisuje do:**
   - **Kolejka:** SQLite `data/jadzia.db` (tabela `tasks`, `sessions`) przez `add_task_to_queue` / `create_operation` w `agent/state.py` i `agent/db.py`.
   - **Przetwarzanie:** W tle **worker loop** w `api.py` (`_worker_loop`) co `WORKER_LOOP_INTERVAL_SECONDS` (domyślnie 15 s) wybiera sesję z kolejki, pobiera `next_task_id`, wywołuje `_run_task_with_timeout( user_input, chat_id, source, task_id, timeout )` → `process_message(..., push_to_telegram=True, auto_advance=False)`.
   - **Zapis do motywu:** W ramach `process_message` → `route_user_input` → węzeł `generate` używa `agent/tools/ssh_orchestrator.write_file()` → SSH/SFTP na serwer (Paramiko) do `BASE_PATH` na hoście z `interfaces/api` / `.env`.

5. **Oczekiwany rezultat:** Użytkownik dostaje najpierw Quick ACK w Telegramie, potem (po planowaniu / generowaniu diffów) prośbę o zatwierdzenie (Tak/Nie) lub gotowy wynik; po zatwierdzeniu – pliki zapisane na serwerze WordPress, ewentualnie weryfikacja deploymentu i komunikat końcowy w Telegramie.

6. **Rzeczywisty rezultat (typowe problemy z dokumentacji i kodu):**
   - Jeśli **TELEGRAM_BOT_TOKEN** nie jest ustawiony na VPS – odpowiedzi (Quick ACK i dalsze) **nie są wysyłane** do użytkownika (tylko zapis do kolejki i worker działają).
   - Jeśli **JWT_SECRET** (lub **TELEGRAM_BOT_JWT_TOKEN**) brak – webhook nie może wywołać Worker API (`create_task` zwróci 401 lub brak tokenu).
   - Historyczny bug (już naprawiony): sesja z pustą `task_queue` i aktywnym `active_task_id` była pomijana przez worker loop; po timeout webhooku zadanie „wisiało”. Obecnie jest ścieżka recovery (empty queue + non-terminal active task → `next_task_id = active_id`).
   - Duplikaty webhooków (retry Telegrama) są odsiewane po `update_id` (TTL 5 min).

---

## 5. LOGI BŁĘDÓW

Ostatnie 20 linii z `logs/agent.log` (JSON Lines). W bieżącym pliku lokalnym **nie ma** wpisów `event_type: "error"` – są to głównie zdarzenia SQLite/state z testów:

```json
{"timestamp": "2026-02-09T21:08:06.335245+00:00", "event_type": "sqlite_read", "message": "[SQLITE] Loaded state for test_worker_123/http: 1 tasks", "operation_id": null, "task_id": null, "data": null}
{"timestamp": "2026-02-09T21:08:06.341312+00:00", "event_type": "sqlite_sync", "message": "[SQLITE] State synced for test_worker_123 (http): 1 tasks", "operation_id": null, "task_id": null, "data": null}
{"timestamp": "2026-02-09T21:08:06.341457+00:00", "event_type": "state_save", "message": "[STATE] Saved state for test_worker_123 (http)", "operation_id": null, "task_id": null, "data": null}
... (powtórzenia sqlite_read / sqlite_sync / state_save dla test_worker_123) ...
{"timestamp": "2026-02-09T21:08:06.391994+00:00", "event_type": "sqlite_read", "message": "[SQLITE] Loaded state for test_worker_123/http: 0 tasks", "operation_id": null, "task_id": null, "data": null}
{"timestamp": "2026-02-09T21:08:06.398109+00:00", "event_type": "sqlite_sync", "message": "[SQLITE] State synced for test_worker_123 (http): 1 tasks", "operation_id": null, "task_id": null, "data": null}
{"timestamp": "2026-02-09T21:08:06.398273+00:00", "event_type": "state_save", "message": "[STATE] Saved state for test_worker_123 (http)", "operation_id": null, "task_id": null, "data": null}
{"timestamp": "2026-02-09T21:08:06.399897+00:00", "event_type": "sqlite_read", "message": "[SQLITE] Loaded state for test_worker_123/http: 1 tasks", "operation_id": null, "task_id": null, "data": null}
{"timestamp": "2026-02-09T21:08:06.402281+00:00", "event_type": "sqlite_read", "message": "[SQLITE] Loaded state for test_worker_123/http: 1 tasks", "operation_id": null, "task_id": null, "data": null}
```

**Uwaga:** Na produkcji (VPS) błędy mogą trafiać także do stdout/stderr (worker_loop, process_message, sendMessage). W raporcie z diagnozy Telegram (`docs/TELEGRAM_FLOW_DIAGNOSIS_REPORT.md`) sugerowane jest sprawdzenie na VPS: `tail -100 /root/jadzia/logs/jadzia-error.log` oraz logów z `worker_loop` i `process_message`.

---

## 6. ISTNIEJĄCE PROBLEMY (lista)

- **Problem 1:** W repozytorium w pliku `.env` **brakuje** zmiennych: `TELEGRAM_BOT_TOKEN`, `JWT_SECRET`, `TELEGRAM_BOT_ENABLED`. Bez nich na środowisku (np. VPS) bot nie wyśle odpowiedzi do Telegrama i Worker API może nie przyjmować żądań z webhooka (401). Konieczne uzupełnienie na serwerze.
- **Problem 2:** Ryzyko **duplikatów zadań** przy retry webhooka Telegrama – łagodzone deduplikacją po `update_id` (TTL 5 min); jeśli retry przyjdzie po dłuższym czasie, teoretycznie możliwy drugi task. W razie problemów warto rozważyć idempotentność po `(chat_id, message_id)` lub `update_id` zapisanym w DB.
- **Problem 3:** **Czas (UTC vs lokalny)** – w regułach projektu wymagane jest UTC; w kodzie używane jest `datetime.now(timezone.utc)` i ISO z timezone. Warto upewnić się, że wszystkie timestampy w DB i logach są spójne (UTC).
- **Problem 4:** **Worker loop** wykonuje się co 15 s (domyślnie); przy jednym zadaniu na sesję Telegram użytkownik może odczuć opóźnienie do ~15 s zanim zadanie zostanie podjęte (po Quick ACK). Można rozważyć krótszy interwał lub osobny trigger przy dodaniu zadania.
- **Problem 5:** **Rollback / SSH** – wrażliwy obszar; zmiany w backup/rollback/SSH powinny być konsultowane (zgodnie z regułami projektu).
- **Problem 6:** Brak pliku **`.env.example`** w repo – trudniej wdrożyć nowe środowisko bez podglądu wymaganych zmiennych (w raporcie powyżej jest struktura do uzupełnienia).
- **Problem 7:** **Schema drift** – przy zmianach w `agent/db.py` (nowe kolumny/tabele) konieczne są migracje (ALTER / skrypty); nie zakładać kolumn „z głowy” bez sprawdzenia schematu i migracji.

---

## 7. PLIKI KONFIGURACYJNE

### requirements.txt

```text
# Jadzia V4 - Production Dependencies
# Generated from pyproject.toml

# Core
anthropic>=0.40.0
fastapi>=0.115.0
PyJWT>=2.8.0
uvicorn[standard]>=0.30.0
pydantic>=2.0.0
pydantic-settings>=2.0.0
python-dotenv>=1.0.0

# SSH & File Operations
paramiko>=3.0.0
filelock>=3.0.0

# Database
python-multipart>=0.0.9

# Testing (optional for production)
pytest>=8.0.0
pytest-asyncio>=0.23.0
httpx>=0.27.0
```

### .env.example (struktura – bez wartości; wartości zastąpione przez XXX)

```env
# Claude API (Anthropic)
ANTHROPIC_API_KEY=XXX

# SSH (WordPress host)
SSH_HOST=XXX
SSH_PORT=XXX
SSH_USER=XXX
SSH_PASSWORD=XXX
SSH_KEY_PATH=XXX
BASE_PATH=XXX
SHOP_URL=XXX
LOCAL_REPO_PATH=XXX

# API
API_HOST=XXX
API_PORT=XXX

# Telegram
TELEGRAM_WEBHOOK_SECRET=XXX
ALLOWED_TELEGRAM_USERS=XXX
TELEGRAM_BOT_TOKEN=XXX
TELEGRAM_BOT_ENABLED=1
JWT_SECRET=XXX
TELEGRAM_BOT_JWT_TOKEN=XXX
TELEGRAM_BOT_API_BASE_URL=XXX

# Legacy (compat with tools)
CYBERFOLKS_HOST=XXX
CYBERFOLKS_PORT=XXX
CYBERFOLKS_USER=XXX
CYBERFOLKS_KEY_PATH=XXX
CYBERFOLKS_BASE_PATH=XXX

# State backend
USE_SQLITE_STATE=1
```

### pyproject.toml

```toml
[project]
name = "jadzia"
version = "1.0.0"
description = "AI agent do zarządzania sklepem internetowym"
requires-python = ">=3.11"
dependencies = [
    "fastapi>=0.109.0",
    "PyJWT>=2.8.0",
    "uvicorn>=0.27.0",
    "httpx>=0.26.0",
    "paramiko>=3.4.0",
    "anthropic>=0.18.0",
    "python-dotenv>=1.0.0",
    "pydantic>=2.5.0",
]

[project.optional-dependencies]
dev = [
    "pytest>=8.0.0",
    "pytest-asyncio>=0.23.0",
]

[tool.pytest.ini_options]
asyncio_mode = "auto"
```

### Inne pliki konfiguracyjne

- **deployment/** – `jadzia.service`, `deploy-to-vps.sh`, `install-service.sh`, `uninstall-service.sh` (nie zmieniane bez wyraźnego polecenia).
- **.env** – jedyny plik z sekretami; nie commitowany (powinien być w .gitignore); na VPS musi zawierać m.in. `TELEGRAM_BOT_TOKEN`, `JWT_SECRET`, `TELEGRAM_BOT_ENABLED=1`.

---

*Raport wygenerowany na podstawie analizy kodu i struktury projektu Jadzia.*
