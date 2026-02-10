# WORKER API DEBUG – przyczyna 404 przy approval

## Kontekst

Webhook Telegram działa, ale przy zatwierdzaniu zmian (approval) klient otrzymuje:

```
❌ Telegram webhook HTTP error 404:
url 'http://127.0.0.1:8000/worker/task/35f7abc1-0d6c-48d4-83f1-39316351c76a/input'
```

---

## 1. Czy endpoint istnieje – TAK

Endpoint jest zdefiniowany w **`interfaces/api.py`** (główna aplikacja FastAPI, bez prefiksu).

**Definicja (linie 437–434):**

```python
@app.post("/worker/task/{task_id}/input")
async def worker_task_input(
    task_id: str, body: WorkerTaskInputRequest, _auth=Depends(verify_worker_jwt)
):
    """
    Submit user input for a task. Only the active task can receive input.
    """
    session = find_session_by_task_id(task_id)
    if not session:
        session = await _resolve_session_for_task(task_id)
    if not session:
        task_after = db_get_task(task_id)
        row_info = (f"chat_id={task_after['chat_id']!r} source={task_after['source']!r}" if task_after else "no row")
        print(f"[worker_task_input] 404 task_id={task_id} db_get_task_after_retry={task_after is not None} {row_info}")
        raise HTTPException(status_code=404, detail="Task not found")
    chat_id, source = session
    active_id = get_active_task_id(chat_id, source)
    if active_id != task_id:
        # Recovery: when active_task_id is None (e.g. ghost-cleared), allow input if task exists in this session
        if active_id is None:
            row = db_get_task(task_id)
            if row and row.get("chat_id") == chat_id and row.get("source") == source:
                pass  # allow request (recovery path)
            else:
                raise HTTPException(
                    status_code=400,
                    detail="Task is queued; input only accepted for the active task",
                )
        else:
            raise HTTPException(
                status_code=400,
                detail="Task is queued; input only accepted for the active task",
            )

    if body.approval is True:
        user_message = "tak"
    elif body.approval is False:
        user_message = "nie"
    elif body.answer is not None:
        user_message = body.answer
    else:
        raise HTTPException(
            status_code=400,
            detail="Provide either 'approval' (true/false) or 'answer' (string)",
        )

    input_kind = "approval" if body.approval is not None else "answer"
    try:
        response_text, awaiting_input, input_type = await process_message(
            user_input=user_message,
            chat_id=chat_id,
            task_id=task_id,
        )
        # ... dalsza logika (status, task_payload, zwrot _task_response_from_task_payload)
```

**Ważne:** 404 jest rzucane **wewnątrz** tego handlera, gdy:

- `find_session_by_task_id(task_id)` zwraca `None`, **oraz**
- `_resolve_session_for_task(task_id)` też zwraca `None`.

`_resolve_session_for_task` robi `db_get_task(task_id)` (nawet z retry po 0.25 s). Czyli **404 = brak wiersza w tabeli `tasks` dla tego `task_id`** (albo stan taki, że sesja nie jest rozpoznawana).

---

## 2. Jak jest wywoływany – `submit_input()` w telegram_worker_client.py

**Pełny kod funkcji `submit_input` (linie 97–117):**

```python
async def submit_input(
    task_id: str,
    jwt_token: str,
    base_url: Optional[str] = None,
    approval: Optional[bool] = None,
    answer: Optional[str] = None,
) -> Dict[str, Any]:
    """
    POST /worker/task/{task_id}/input with approval and/or answer.
    Raises httpx.HTTPStatusError on 4xx/5xx.
    """
    url = (base_url or get_base_url()).rstrip("/") + f"/worker/task/{task_id}/input"
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}
    body: Dict[str, Any] = {}
    if approval is not None:
        body["approval"] = approval
    if answer is not None:
        body["answer"] = answer
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        r = await client.post(url, json=body, headers=headers)
        r.raise_for_status()
        return r.json()
```

**Budowany URL:**

- Bazowy URL: `get_base_url()` → z env `TELEGRAM_BOT_API_BASE_URL` lub domyślnie `http://127.0.0.1:8000`.
- Ścieżka: `"/worker/task/" + task_id + "/input"`.
- **Pełny URL:** `http://127.0.0.1:8000/worker/task/35f7abc1-0d6c-48d4-83f1-39316351c76a/input` – zgadza się z komunikatem błędu.

---

## 3. Czy task istnieje w DB – do sprawdzenia na VPS

Na serwerze (VPS) uruchom:

```bash
cd /root/jadzia
source venv/bin/activate
python3 << 'EOF'
import sys
sys.path.insert(0, '.')
from agent.db import db_get_task

task_id = "35f7abc1-0d6c-48d4-83f1-39316351c76a"
task = db_get_task(task_id)
print(f"Task {task_id}:")
print(f"  exists: {task is not None}")
if task:
    print(f"  status: {task.get('status')}")
    print(f"  chat_id: {task.get('chat_id')}")
    print(f"  source: {task.get('source')}")
    print(f"  created_at: {task.get('created_at')}")
EOF
```

- Jeśli **exists: False** – to wyjaśnia 404: handler nie znajduje zadania w DB i rzuca `HTTPException(404, "Task not found")`.
- Jeśli **exists: True** – wtedy 404 nie powinno wynikać z braku taska; warto sprawdzić logi serwera (`[worker_task_input] 404 ...`) oraz czy używany jest ten sam plik bazy co worker.

---

## 4. Lista wszystkich Worker API endpoints

Wszystkie są w **`interfaces/api.py`**, na głównym `app` (bez prefiksu):

| Metoda | Ścieżka | Opis |
|--------|---------|------|
| POST   | `/worker/task` | Utworzenie zadania (quick ACK) |
| GET    | `/worker/task/{task_id}` | Status zadania |
| POST   | `/worker/task/{task_id}/input` | Wysłanie inputu (approval/answer) – **tu występuje 404** |
| POST   | `/worker/tasks/cleanup` | Ręczne oznaczenie zadań jako failed |
| GET    | `/worker/health` | Health check |
| GET    | `/worker/dashboard` | Dashboard (wymaga JWT) |

Żaden z tych route’ów nie jest rejestrowany warunkowo (w przeciwieństwie do routera Telegram przy `TELEGRAM_BOT_ENABLED=1`). Trasa **POST /worker/task/{task_id}/input** jest zawsze zarejestrowana.

---

## 5. Porównanie URL

| Źródło | URL |
|--------|-----|
| **telegram_worker_client.submit_input()** | `{base_url}/worker/task/{task_id}/input` → np. `http://127.0.0.1:8000/worker/task/35f7abc1-0d6c-48d4-83f1-39316351c76a/input` |
| **FastAPI (api.py)** | `@app.post("/worker/task/{task_id}/input")` → ta sama ścieżka |

URL jest **zgodny**. 404 nie wynika z błędnej ścieżki ani braku rejestracji endpointu.

---

## Wnioski i rekomendacje

1. **Endpoint istnieje i ścieżka jest poprawna** – 404 nie jest „route not found” ze strony FastAPI.
2. **404 pochodzi z handlera** – gdy dla danego `task_id` nie zostanie znaleziona sesja (czyli w praktyce brak rekordu w `tasks` lub brak dopasowania po `db_get_task` w `_resolve_session_for_task`).
3. **Najbardziej prawdopodobna przyczyna:** w momencie wywołania approval **zadanie o tym `task_id` nie istnieje w tabeli `tasks`** (np. inna baza, opóźnienie zapisu, lub task nigdy nie został zapisany dla tej sesji/źródła).
4. **Na VPS należy:**
   - Uruchomić skrypt z sekcji 3 i potwierdzić, czy task istnieje w DB.
   - Sprawdzić w logach Jadzi (np. `logs/jadzia.log`, `logs/agent.log`) wpisy `[worker_task_input] 404 task_id=...` – potwierdzą one, że to 404 z handlera i czy `db_get_task_after_retry` był True/False.
   - Upewnić się, że `USE_SQLITE_STATE=1` i że worker oraz webhook używają tej samej bazy (`data/jadzia.db`).
5. **Opcjonalnie:** dodać krótkie logowanie na wejściu do `worker_task_input` (np. `task_id`, wynik `db_get_task(task_id)`), żeby w logach było widać, czy request w ogóle dociera i co zwraca DB.

Raport wygenerowany na podstawie: `interfaces/api.py`, `interfaces/telegram_worker_client.py`, `agent/state.py`, `agent/db.py`.
