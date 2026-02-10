# JADZIA - SYSTEM BIBLE
## Ostatnia aktualizacja: 2026-02-09
## Wersja: 1.0

---

# 1. ARCHITEKTURA (PRAWDA ABSOLUTNA)

## 1.1 Flow komendy /zadanie

```
[USER]
  ↓ wysyła "/zadanie zmień kolor"
[TELEGRAM API]
  ↓ webhook POST /telegram/webhook
[telegram_api.py]
  ↓ _handle_webhook_request()
  ↓ create_task() → zwraca task_id
  ↓ NATYCHMIAST odpowiada "Przyjęto zadanie"
[SQLite Queue]
  ↓ task zapisany ze statusem "queued" / "pending"
[Worker Loop] (interfaces/api.py, _worker_loop)
  ↓ pobiera task z kolejki
  ↓ process_message()
[SSH Orchestrator]
  ↓ read_file() / write_file()
  ↓ backup + zapis
[send_awaiting_response_to_telegram()]
  ↓ push wyniku do Telegram
[USER] otrzymuje wynik
```

## 1.2 Statusy zadania

- `queued` – w kolejce, czeka na worker
- `planning` – worker przetwarza (planowanie)
- `reading_files` / `generating_code` – generowanie diffów
- `plan_approval` – czeka na zatwierdzenie planu (awaiting_type)
- `diff_ready` – czeka na zatwierdzenie zmian (pokazuje diff)
- `approved` – user zatwierdził
- `writing_files` – zapisuję na serwer
- `completed` – sukces, plik zapisany
- `failed` – błąd
- `rolled_back` – wycofane

**Uwaga:** Pełna lista stałych w `agent/state.py` – klasa `OperationStatus`.

## 1.3 Źródło prawdy o task_id

**JEDYNE źródło prawdy: SQLite – tabele `sessions` i `tasks`**

Tabela `sessions`: `active_task_id`, `task_queue` dla danej pary (chat_id, source).
Tabela `tasks`: task_id, chat_id, source, status, created_at, updated_at, itd.

**ZAKAZANE:** używanie in-memory dict jako źródła prawdy dla task_id.

---

# 2. KONWENCJE KODU

## 2.1 Logowanie

KAŻDY log MUSI zawierać kontekst (task_id, chat_id, status, operation_id gdy dotyczy).

Formaty prefiksów:
- `[Telegram]` – interfejs Telegram
- `[Worker]` – worker loop
- `[SSH]` – operacje SSH
- `[DB]` – operacje bazy danych

Przykład:
```python
logger.info("[Telegram] akcja", extra={
    "task_id": task_id,
    "chat_id": chat_id,
    "status": status,
    "operation_id": op_id
})
```

## 2.2 Error handling

```python
try:
    # operacja
except SpecificError as e:
    logger.error("[KOMPONENT] opis błędu", extra={"task_id": task_id, ...})
    # NIE: raise generic Exception
    # TAK: return {"error": "opis", "task_id": task_id}
```

## 2.3 Nazewnictwo

- `chat_id` = `"telegram_{user_id}"` – identyfikator sesji Jadzi
- `numeric_id` = sam user_id – do Telegram Bot API (sendMessage)
- `task_id` = UUID zadania
- `operation_id` = UUID operacji (może być wiele na task)

---

# 3. PLIKI KRYTYCZNE

## 3.1 telegram_api.py (interfaces/telegram_api.py)

**ODPOWIADA ZA:**
- Odbieranie webhooków
- Walidację użytkownika
- Parsowanie komend
- Tworzenie tasków (create_task)
- Wysyłanie odpowiedzi do Telegram

**NIE ODPOWIADA ZA:**
- Przetwarzanie tasków (to robi worker)
- Operacje SSH (to robi ssh_orchestrator)
- Logikę biznesową

## 3.2 ssh_orchestrator.py (agent/tools/ssh_orchestrator.py)

**ODPOWIADA ZA:**
- Połączenie SSH
- Odczyt/zapis plików
- Backup przed zapisem
- Walidację bezpieczeństwa PHP

**NIE ODPOWIADA ZA:**
- Logikę kolejki
- Komunikację z Telegram

## 3.3 Worker loop (interfaces/api.py)

**ODPOWIADA ZA:**
- Pobieranie tasków z kolejki
- Wywoływanie process_message()
- Aktualizację statusu
- Push wyniku do Telegram (przez process_message → send_awaiting_response_to_telegram)

Funkcja: `_worker_loop()`. Uruchomienie: w `startup()` przez `asyncio.create_task(_worker_loop())`.

---

# 4. BAZA DANYCH

## 4.1 Tabela sessions

```sql
CREATE TABLE IF NOT EXISTS sessions (
    chat_id TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'http',
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    active_task_id TEXT,
    task_queue TEXT NOT NULL DEFAULT '[]',
    UNIQUE(chat_id, source)
);
```

## 4.2 Tabela tasks

```sql
CREATE TABLE IF NOT EXISTS tasks (
    task_id TEXT PRIMARY KEY,
    chat_id TEXT NOT NULL,
    source TEXT NOT NULL DEFAULT 'http',
    operation_id TEXT NOT NULL,
    status TEXT NOT NULL,
    user_input TEXT,
    dry_run INTEGER NOT NULL DEFAULT 0,
    test_mode INTEGER NOT NULL DEFAULT 0,
    webhook_url TEXT,
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL,
    completed_at TEXT,
    plan TEXT,
    diffs TEXT,
    new_contents TEXT,
    written_files TEXT,
    errors TEXT,
    pending_plan TEXT,
    validation_errors TEXT,
    retry_count INTEGER NOT NULL DEFAULT 0,
    deploy_result TEXT,
    awaiting_response INTEGER NOT NULL DEFAULT 0,
    awaiting_type TEXT,
    pending_plan_with_questions TEXT,
    last_response TEXT,
    files_to_modify TEXT,
    FOREIGN KEY (chat_id, source) REFERENCES sessions(chat_id, source)
);

CREATE INDEX IF NOT EXISTS idx_tasks_chat_source ON tasks(chat_id, source);
CREATE INDEX IF NOT EXISTS idx_tasks_task_id ON tasks(task_id);
```

## 4.3 Tabela file_operations (proponowana / opcjonalna)

Do ewentualnego wprowadzenia – audyt zapisów plików per task.

```sql
CREATE TABLE file_operations (
    id INTEGER PRIMARY KEY,
    task_id TEXT,
    path TEXT,
    backup_path TEXT,
    operation TEXT,
    created_at TIMESTAMP
);
```

---

# 5. ZMIENNE ŚRODOWISKOWE

## 5.1 Wymagane

- `TELEGRAM_BOT_TOKEN` – token bota Telegram (do wysyłania odpowiedzi)
- `JWT_SECRET` – sekret do JWT (Worker API)
- `ANTHROPIC_API_KEY` – Claude API
- `SSH_HOST` – host SSH
- `SSH_USER` – user SSH
- `SSH_PASSWORD` lub `SSH_KEY_PATH` – dostęp SSH
- `BASE_PATH` – ścieżka do WordPress na serwerze

## 5.2 Opcjonalne

- `SSH_PORT` (domyślnie 22)
- `TELEGRAM_WEBHOOK_SECRET` – dla n8n / walidacji webhooka
- `ALLOWED_TELEGRAM_USERS` – whitelist user_id (np. 6746343970)
- `TELEGRAM_BOT_ENABLED=1` – włącza router /telegram
- `TELEGRAM_BOT_JWT_TOKEN` – alternatywa do JWT_SECRET dla bota
- `TELEGRAM_BOT_API_BASE_URL` – URL Worker API (domyślnie http://127.0.0.1:8000)
- `USE_SQLITE_STATE=1` – stan w SQLite
- `SHOP_URL` – URL sklepu (health check)
- `API_HOST`, `API_PORT` – serwer API

---

# 6. ZASADY NIENARUSZALNE

- **JEDEN task_id = JEDEN przepływ** – nie twórz nowego task_id w środku przetwarzania.
- **BACKUP PRZED ZAPISEM** – zawsze, bez wyjątków.
- **LOG Z CONTEXT** – każdy log z task_id i chat_id (gdy dotyczy).
- **SQLITE = ŹRÓDŁO PRAWDY** – nie in-memory dict dla task_id.
- **ATOMOWOŚĆ** – albo cała operacja, albo rollback.
- **TIMEOUT NA SSH** – max 30s na operację.
