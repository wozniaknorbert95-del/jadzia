## Jadzia V4 – Operations Guide

**Cel:** praktyczny opis obsługi produkcyjnej Jadzia V4 na VPS (`185.243.54.115:8000`), z naciskiem na Worker API, monitoring i podstawowe komendy operacyjne.

---

## 1. Środowisko produkcyjne

- **VPS (API):** `http://185.243.54.115:8000`
- **Katalog aplikacji (VPS):** `/root/jadzia`
- **Service:** `jadzia` (systemd)
- **Baza:** SQLite – plik `data/jadzia.db` na VPS

Podstawowe komendy na VPS (z lokalnej maszyny):

```bash
# SSH na VPS
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115

# Status serwisu
sudo systemctl status jadzia

# Restart serwisu
sudo systemctl restart jadzia

# Ostatnie logi aplikacji
tail -50 /root/jadzia/logs/jadzia.log
tail -50 /root/jadzia/logs/jadzia-error.log
```

---

## 2. Uwierzytelnianie Worker API (JWT)

Worker API (`/worker/...`) korzysta z JWT, gdy ustawiony jest `JWT_SECRET`:

- Jeśli **`JWT_SECRET` jest ustawiony** – wszystkie endpointy Worker API wymagają nagłówka:

```http
Authorization: Bearer <JWT_TOKEN>
```

- Jeśli **`JWT_SECRET` nie jest ustawiony** – uwierzytelnianie jest wyłączone (tryb dev/CI). **Na produkcji wymagane jest JWT.**

### 2.1. Generowanie tokena JWT

Na maszynie, gdzie dostępny jest kod Jadzia (np. lokalnie):

```bash
cd /ścieżka/do/Jadzia
export JWT_SECRET="<JWT_SECRET>"
python scripts/jwt_token.py --days 30
```

Outputem będzie token do użycia jako `<JWT_TOKEN>` w nagłówku Authorization.

---

## 3. Worker API – 6 kluczowych endpointów

Base URL dla Worker API:

```text
http://185.243.54.115:8000
```

### 3.1. POST /worker/task – utworzenie zadania

- **Metoda:** `POST`
- **Ścieżka:** `/worker/task`
- **Auth:** `Authorization: Bearer <JWT_TOKEN>` (gdy `JWT_SECRET` ustawiony)
- **Body (JSON):**

```json
{
  "instruction": "napraw stronę główną",
  "chat_id": "shop_prod_1",
  "webhook_url": "https://example.com/webhook-optional",
  "test_mode": false
}
```

- **Query:** `dry_run` (bool, domyślnie `false`) – podgląd bez zapisu plików.
- **Odpowiedź 200 (WorkerTaskCreateResponse):**
  - `task_id` – UUID zadania
  - `status` – `"queued"` lub `"processing"`
  - `position_in_queue` – `0` = przetwarzane, `>0` = w kolejce
  - `chat_id`
  - `dry_run`
  - `test_mode`

**Przykład:**

```bash
curl -X POST "http://185.243.54.115:8000/worker/task?dry_run=true" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "instruction": "Zmień kolor przycisku CTA na zielony",
    "chat_id": "shop_prod_1",
    "webhook_url": "https://example.com/jadzia-webhook",
    "test_mode": false
  }'
```

---

### 3.2. GET /worker/task/{task_id} – status zadania

- **Metoda:** `GET`
- **Ścieżka:** `/worker/task/{task_id}`
- **Auth:** `Authorization: Bearer <JWT_TOKEN>`
- **Odpowiedź 200:**
  - `task_id`
  - `status` – jedno z:
    - `"in_progress"`
    - `"diff_ready"`
    - `"completed"`
    - `"error"`
  - `position_in_queue` – `0` lub numer w kolejce
  - `awaiting_input` – czy agent czeka na odpowiedź użytkownika
  - `input_type` – np. `"approval"` lub `"answer_questions"`
  - `response` – ostatnia odpowiedź agenta
  - `operation` – szczegóły operacji (plan, diffy, itp.)
  - `dry_run`, `test_mode`

**Przykład:**

```bash
curl "http://185.243.54.115:8000/worker/task/<TASK_ID>" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

### 3.3. POST /worker/task/{task_id}/input – odpowiedź użytkownika

- **Metoda:** `POST`
- **Ścieżka:** `/worker/task/{task_id}/input`
- **Auth:** `Authorization: Bearer <JWT_TOKEN>`
- **Body (JSON) – wymagane jedno z:**
  - `{"approval": true}` – odpowiedź „tak”
  - `{"approval": false}` – odpowiedź „nie”
  - `{"answer": "dowolny tekst"}` – odpowiedź tekstowa

- **Zasady:**
  - Input akceptowany **tylko** dla **aktywnego** zadania (`400` gdy zadanie jest w kolejce).
  - Brak `approval` i `answer` → `400 Bad Request`.

**Przykład (zatwierdzenie planu):**

```bash
curl -X POST "http://185.243.54.115:8000/worker/task/<TASK_ID>/input" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{"approval": true}'
```

---

### 3.4. POST /worker/tasks/cleanup – ręczne oznaczenie zadań jako failed

- **Metoda:** `POST`
- **Ścieżka:** `/worker/tasks/cleanup`
- **Auth:** `Authorization: Bearer <JWT_TOKEN>`
- **Body (JSON):**

```json
{
  "task_ids": ["<TASK_ID_1>", "<TASK_ID_2>"],
  "reason": "manual_cleanup"
}
```

- **Odpowiedź 200 (WorkerTasksCleanupResponse):**
  - `updated` – lista tasków oznaczonych jako failed
  - `skipped_terminal` – taski już zakończone (nie zmienione)
  - `not_found` – nieistniejące taski

**Przykład:**

```bash
curl -X POST "http://185.243.54.115:8000/worker/tasks/cleanup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "task_ids": ["<TASK_ID_1>", "<TASK_ID_2>"],
    "reason": "manual_cleanup"
  }'
```

---

### 3.5. GET /worker/health – health check Workera

- **Metoda:** `GET`
- **Ścieżka:** `/worker/health`
- **Auth:** brak (publiczny health check)
- **Odpowiedź 200 (JSON):**
  - `status` – `"healthy"` lub `"degraded"` (bazuje m.in. na wyniku testu SSH)
  - `uptime_seconds`
  - `active_sessions`
  - `active_tasks`
  - `queue_length`
  - `total_tasks`
  - `ssh_connection` – `"ok"` / `"error"`
  - `sqlite_connection` – wynik `db_health_check()` (True/False lub szczegóły)
  - `last_success`
  - `errors_last_hour`
  - `failed_tasks_total`
  - `last_deployment_verification` – `{ "timestamp", "healthy", "auto_rollback_count" }`

**Przykład:**

```bash
curl "http://185.243.54.115:8000/worker/health"
```

---

### 3.6. GET /worker/dashboard – metryki zadań (SQLite)

- **Metoda:** `GET`
- **Ścieżka:** `/worker/dashboard`
- **Auth:** `Authorization: Bearer <JWT_TOKEN>`
- **Zachowanie:**
  - Gdy `USE_SQLITE_STATE=1` i DB działa – zwraca statystyki z `db_get_dashboard_metrics()`.
  - Gdy `USE_SQLITE_STATE=0` – pusta odpowiedź z `sqlite_required=true`.
  - Gdy błąd SQLite – pusta odpowiedź z `error="db_unavailable"`.

- **Pola odpowiedzi:**
  - `total_tasks`
  - `by_status` – liczba zadań wg API statusów (`completed`, `error`, `in_progress`, `diff_ready`)
  - `test_mode_tasks`
  - `production_tasks`
  - `recent_tasks` – lista ostatnich zadań (status, czasy)
  - `errors_last_24h`
  - `avg_duration_seconds`
  - opcjonalnie: `sqlite_required`, `error`

**Przykład:**

```bash
curl "http://185.243.54.115:8000/worker/dashboard" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

---

## 4. Pozostałe endpointy operacyjne

Te endpointy nie należą do „szóstki” Worker API, ale są kluczowe operacyjnie.

- **GET `/`** – prosty health check API

```bash
curl "http://185.243.54.115:8000/"
```

- **POST `/chat`** – główny endpoint dialogowy (Telegram/n8n)
- **GET `/status`** – status bieżącej operacji (domyślny `chat_id="default"`)
- **POST `/rollback`** – wykonanie rollbacku ostatnich zmian (patrz `RECOVERY.md`)
- **GET `/health`** – health check sklepu (`SHOP_URL`) przez HTTP
- **GET `/logs`** – ostatnie logi z `logs/agent.log`
- **POST `/clear`** – awaryjne czyszczenie stanu + force unlock
- **GET `/test-ssh`** – test połączenia SSH z hostingiem WordPress
- **GET `/costs`** – aktualne statystyki tokenów i kosztów (z `agent.agent`)
- **POST `/costs/reset`** – resetowanie liczników kosztów
- **GET `/costs/estimate?tokens=1000`** – kalkulator kosztu tokenów

---

## 5. Monitoring i alerty

### 5.1. Logi

Na VPS:

```bash
cd /root/jadzia
tail -f logs/jadzia.log
tail -f logs/jadzia-error.log
```

Endpoint HTTP:

```bash
curl "http://185.243.54.115:8000/logs?limit=50"
```

### 5.2. Discord alerts

Plik: `agent/alerts.py`

- Env: `DISCORD_WEBHOOK_URL="<DISCORD_WEBHOOK_URL>"`
- Alerty wysyłane asynchronicznie (daemon thread), brak blokowania głównego flow.
- Typowe alerty:
  - `"rollback_executed"` / `"rollback_failed"` (z `/rollback` i `agent.nodes.commands`)
  - `"task_failed"` (z `agent.nodes.planning` i `agent.nodes.approval`)

Format wiadomości zawiera typ, task_id, timestamp i szczegóły błędu.

### 5.3. Koszty Claude

Endpointy `/costs`, `/costs/reset`, `/costs/estimate` bazują na licznikach w `agent.agent`:

```bash
curl "http://185.243.54.115:8000/costs"
curl -X POST "http://185.243.54.115:8000/costs/reset"
curl "http://185.243.54.115:8000/costs/estimate?tokens=50000"
```

---

## 6. Dzienna checklista operacyjna

1. **Health Worker API**
   - `curl http://185.243.54.115:8000/worker/health`
   - Oczekiwane: `status="healthy"`, `ssh_connection="ok"`, sensowny `uptime_seconds`.
2. **Dashboard zadań**
   - `curl http://185.243.54.115:8000/worker/dashboard -H "Authorization: Bearer <JWT_TOKEN>"`
   - Sprawdź, czy nie rośnie liczba `error` i `errors_last_24h`.
3. **Health sklepu**
   - `curl http://185.243.54.115:8000/health`
   - Oczekiwane: `status="ok"`.
4. **Logi krytyczne**
   - `tail -50 /root/jadzia/logs/jadzia-error.log`
5. **Alerty Discord**
   - Sprawdź kanał Discord czy nie pojawiły się nowe alerty `"task_failed"` / `"rollback_failed"`.

