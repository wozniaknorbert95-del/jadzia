# JADZIA - ROADMAP NAPRAWY
## Data utworzenia: 2026-02-09

---

# FAZA 0: DIAGNOSTYKA (30 min)

## Task 0.1: Zrzut stanu bazy

```bash
sqlite3 data/jadzia.db ".schema"
sqlite3 data/jadzia.db "SELECT task_id, chat_id, status, created_at FROM tasks ORDER BY created_at DESC LIMIT 20;"
```

## Task 0.2: Sprawdzenie logów

```bash
tail -100 logs/agent.log | grep -E "(ERROR|WARN|task_id)"
```

## Task 0.3: Test połączenia SSH

```python
from agent.tools.ssh_orchestrator import read_file, HOST, USER
print(f"SSH: {USER}@{HOST}")
result = read_file("wp-config.php")
print("SSH OK" if result else "SSH FAIL")
```

---

# FAZA 1: STABILIZACJA (2h)

## Task 1.1: Usuń in-memory cache task_id

**PLIK:** interfaces/telegram_api.py

**USUŃ:** słownik `_telegram_chat_to_task_id: dict[str, str] = {}` oraz wszystkie zapisy do niego i odczyty.

**ZASTĄP:** odczyty aktywnego task_id wywołaniem funkcji z warstwy DB. Wymaga wcześniejszego **Task 1.1b**.

**Task 1.1b (w agent/db.py):** Dodać funkcję `db_get_active_task(chat_id: str, source: str) -> Optional[str]`, która zwraca `active_task_id` z tabeli `sessions`:

```python
def db_get_active_task(chat_id: str, source: str = "http") -> Optional[str]:
    """Return active_task_id for session from sessions table. Single source of truth."""
    conn = get_connection()
    row = conn.execute(
        "SELECT active_task_id FROM sessions WHERE chat_id = ? AND source = ?",
        (chat_id, source),
    ).fetchone()
    return row["active_task_id"] if row and row["active_task_id"] else None
```

Następnie w telegram_api.py: zamiast `_telegram_chat_to_task_id.get(chat_id)` używać `db_get_active_task(chat_id, "telegram")`. Fallback na `db_get_last_active_task(chat_id, "telegram")` gdy potrzebne (np. gdy active_task_id jest None ale jest nieterminalne zadanie).

## Task 1.2: Jeden sposób szukania task_id

**PLIK:** interfaces/telegram_api.py

**ZASTĄP** funkcję `_get_task_id_for_chat`:

```python
def _get_task_id_for_chat(chat_id: str) -> Optional[str]:
    """Get active task_id for chat from DB only."""
    from agent.db import db_get_active_task, db_get_task
    task_id = db_get_active_task(chat_id, "telegram")
    if task_id:
        # Zweryfikuj że task istnieje w tasks
        if db_get_task(task_id) is not None:
            return task_id
    # Fallback: ostatnie nieterminalne zadanie (np. po restarcie gdy sessions nie ma active_task_id)
    last = db_get_last_active_task(chat_id, "telegram")
    return last.get("task_id") if last else None
```

## Task 1.3: Structured logging

**DODAJ** na początku kluczowych ścieżek w telegram_api.py:

```python
logger.info("[Telegram] %s started", func_name, extra={
    "task_id": task_id,
    "chat_id": chat_id,
    "command": command
})
```

## Task 1.4: Retry logic dla SSH

**PLIK:** agent/tools/ssh_orchestrator.py

**SPRAWDŹ** czy `@with_retry` działa (read_file, write_file już go używają). Test: odłącz sieć na 2s, sprawdź czy retry zadziała.

---

# FAZA 2: UPROSZCZENIE (3h)

## Task 2.1: Połącz callback i approval

**PLIK:** interfaces/telegram_api.py

Obie ścieżki (callback z przycisków Tak/Nie oraz approval z tekstu "tak"/"nie") robią to samo – wywołanie `submit_input(task_id, ..., approval=...)`. Połącz w jedną funkcję:

```python
async def _handle_approval(chat_id: str, task_id: str, approved: bool) -> TelegramWebhookResponse:
    # jedna logika dla przycisków i tekstu
```

## Task 2.2: Uprość flow statusów

**OBECNE:** Wiele statusów (queued, planning, reading_files, generating_code, diff_ready, approved, writing_files, completed, failed, rolled_back).

**DOCELOWE (opcjonalnie):** Uproszczenie do 5 statusów widocznych dla użytkownika: `pending` → `processing` → `awaiting_approval` → `completed` / `failed`. Mapowanie wewnętrzne pozostaje w OperationStatus.

## Task 2.3: Health check endpoint

**DODAJ** endpoint (np. rozszerzenie istniejącego `/health` lub `/worker/health`), który sprawdza:

- DB connection (SQLite)
- SSH connection
- Telegram token validity (opcjonalnie)
- Worker loop status (czy działa)

---

# FAZA 3: CZYSZCZENIE (1h)

## Task 3.1: Usuń martwy kod

- Sprawdź wszystkie `# TODO`
- Usuń zakomentowany kod
- Usuń nieużywane importy

## Task 3.2: Utwórz .env.example

```
TELEGRAM_BOT_TOKEN=your_token_here
JWT_SECRET=generate_random_secret
ANTHROPIC_API_KEY=your_key
SSH_HOST=your_host
SSH_USER=your_user
SSH_PASSWORD=your_password
BASE_PATH=/home/user/public_html
TELEGRAM_WEBHOOK_SECRET=optional
ALLOWED_TELEGRAM_USERS=123,456
USE_SQLITE_STATE=1
```

## Task 3.3: Dokumentacja deployment

**README.md** (lub docs/) z sekcjami:

- Wymagania
- Instalacja
- Konfiguracja (.env)
- Troubleshooting

---

# WERYFIKACJA

Po każdej fazie:

1. Wyślij `/zadanie test` w Telegram.
2. Sprawdź logi: `tail -f logs/agent.log`.
3. Sprawdź czy plik się zapisał na serwerze (jeśli dotyczy): `ls -la` w BASE_PATH.
4. Sprawdź czy odpowiedź wróciła do Telegram.
