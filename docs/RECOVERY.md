## Jadzia V4 – Recovery Guide

**Cel:** procedury odtwarzania działania systemu po awariach Worker API, sklepu, SQLite, SSH i rollback engine. Oparte wyłącznie na aktualnym kodzie (`interfaces/api.py`, `agent/tools/rest.py`, `agent/alerts.py`, `agent/state.py`, `docs/PHASE5_ROLLBACK.md`).

---

## 1. Kluczowe komponenty i sygnały awarii

- **Worker API (FastAPI)**
  - Endpointy: `/worker/task`, `/worker/task/{task_id}`, `/worker/task/{task_id}/input`, `/worker/tasks/cleanup`, `/worker/health`, `/worker/dashboard`.
  - Health: `/worker/health` (`status`, `ssh_connection`, `sqlite_connection`, kolejki).

- **Rollback engine**
  - Funkcja `rollback()` w `agent.tools.rest`:
    - Korzysta z backupów z `agent.state.get_backups(...)`.
    - Przywraca pliki na WordPressie przez SSH (`read_file_ssh_bytes` → `write_file_ssh_bytes`).
  - Endpoint: `POST /rollback`.

- **SQLite state / dashboard**
  - `USE_SQLITE_STATE` w `agent.state` oraz `docs/PHASE5_ROLLBACK.md`.
  - Metryki zadań: `db_get_worker_health_session_counts`, `db_get_dashboard_metrics`.

- **Discord alerts**
  - `agent.alerts.send_alert()` – typy: `rollback_executed`, `rollback_failed`, `task_failed`.

---

## 2. Worker API niedostępne (5xx, timeout, brak odpowiedzi)

### 2.1. Detekcja

- `curl http://185.243.54.115:8000/worker/health` zwraca błąd HTTP/timeout.
- `curl http://185.243.54.115:8000/` również nie działa.

### 2.2. Kroki naprawcze (na VPS)

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115

# 1. Sprawdź status serwisu
sudo systemctl status jadzia

# 2. Zbierz ostatnie logi
tail -100 /root/jadzia/logs/jadzia.log
tail -100 /root/jadzia/logs/jadzia-error.log

# 3. Jeśli usługa nie działa – uruchom ponownie
sudo systemctl restart jadzia

# 4. Ponów health check
curl http://localhost:8000/worker/health
```

### 2.3. Oczekiwany efekt

- `curl http://185.243.54.115:8000/worker/health` zwraca JSON z `status: "healthy"` lub `"degraded"` zamiast timeoutu.

---

## 3. Status "degraded" w /worker/health

Kod w `interfaces/api.py`:

- `status = "healthy" if ssh_status == "ok" else "degraded"`
- `ssh_status` z `test_ssh_connection()` (w `agent.tools.rest`).
- `sqlite_connection` z `db_health_check()`.

### 3.1. Diagnoza SSH (ssh_connection="error")

```bash
curl http://185.243.54.115:8000/test-ssh
```

Oczekiwane:

- `{"status": "ok", "message": "Polaczenie SSH dziala"}` – SSH OK.

Jeśli `status="error"` lub komunikat `Brak konfiguracji SSH w .env`:

1. Zaloguj się na VPS:

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115
cd /root/jadzia
cat .env
```

2. Zweryfikuj zmienne:

- `SSH_HOST` / `CYBERFOLKS_HOST`
- `SSH_PORT` / `CYBERFOLKS_PORT`
- `SSH_USER` / `CYBERFOLKS_USER`
- `SSH_PASSWORD` lub `SSH_KEY_PATH` / `CYBERFOLKS_KEY_PATH`

3. Popraw `.env` (z użyciem prawidłowych wartości, bez ujawniania haseł) i zrestartuj serwis:

```bash
sudo systemctl restart jadzia
curl http://localhost:8000/test-ssh
curl http://localhost:8000/worker/health
```

### 3.2. Problemy SQLite (sqlite_connection=False / błąd)

Jeśli `/worker/health` zwraca `sqlite_connection` jako błąd:

1. Na VPS:

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115
cd /root/jadzia

# Czy plik istnieje
ls -l data/jadzia.db

# Próba otwarcia bazy
sqlite3 data/jadzia.db ".tables"
```

2. Jeśli plik uszkodzony / brak:
   - Sprawdź, czy istnieje backup (`deploy-to-vps.sh` robi kopie `jadzia.db.bak.*` przed aktualizacją kodu).

```bash
ls -1 data/jadzia.db.bak.*
cp data/jadzia.db.bak.<YYYYMMDD-HHMMSS> data/jadzia.db
sudo systemctl restart jadzia
curl http://localhost:8000/worker/health
```

3. Jeśli chcesz wrócić do JSON state (Phase 4) – patrz `docs/PHASE5_ROLLBACK.md`.

---

## 4. Zadania zablokowane / kolejka nie idzie

Symptomy:

- `/worker/task/{task_id}` cały czas `status="in_progress"` / `awaiting_input=true`, brak ruchu.
- Kolejne zadania mają rosnące `position_in_queue`.

### 4.1. Wymuszone oznaczenie zadań jako failed

1. Zidentyfikuj `task_id` z dashboardu lub logów.
2. Użyj endpointu cleanup:

```bash
curl -X POST "http://185.243.54.115:8000/worker/tasks/cleanup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "task_ids": ["<TASK_ID_1>", "<TASK_ID_2>"],
    "reason": "manual_cleanup"
  }'
```

3. Zweryfikuj status zadań:

```bash
curl "http://185.243.54.115:8000/worker/task/<TASK_ID_1>" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

### 4.2. Awaryjne wyczyszczenie stanu sesji

Endpoint `POST /clear` robi:

- `force_unlock()` – usuwa lock agenta.
- `clear_state()` – czyści aktualny stan.

Użycie:

```bash
curl -X POST "http://185.243.54.115:8000/clear"
```

Po czyszczeniu nowe zadania będą obsługiwane od zera.

---

## 5. Błąd po deployu – rollback zmian na WordPressie

Rollback engine jest zaimplementowany w `agent.tools.rest.rollback()` i używany przez:

- Endpoint `POST /rollback` w `interfaces/api.py`.
- Węzeł komend w `agent.nodes.commands`.

### 5.1. Kiedy używać

- Po wdrożeniu (deploy) strona sklepu działa niepoprawnie (błędy PHP, biały ekran, brak stylów).
- Pojawił się alert Discord `"rollback_failed"` / `"task_failed"` dotyczący zmian w plikach.

### 5.2. Standardowa procedura rollback (HTTP)

1. Sprawdź health sklepu:

```bash
curl "http://185.243.54.115:8000/health"
```

2. Jeśli `status != "ok"`, wykonaj rollback:

```bash
curl -X POST "http://185.243.54.115:8000/rollback"
```

3. Odpowiedź (`RollbackResponse`):
   - `status` – `"ok"`, `"partial"` lub `"error"`
   - `restored` – lista ścieżek przywróconych plików
   - `errors` – lista błędów przy przywracaniu
   - `message` – opisowy komunikat

4. Zweryfikuj:

```bash
curl "http://185.243.54.115:8000/health"
curl "http://185.243.54.115:8000/worker/health"
```

### 5.3. Co dokładnie robi rollback()

Zgodnie z `agent.tools.rest.rollback`:

- Pobiera mapę backupów z `get_backups(chat_id, source)`.
- Dla każdego pliku:
  - Czyta zawartość z backupu przez SSH (`read_file_ssh_bytes`).
  - Wyznacza bezpieczną ścieżkę docelową (`get_safe_path(BASE_PATH, original_path)`).
  - Zapisuje plik na WordPressie (`write_file_ssh_bytes`).
- Loguje event `ROLLBACK` z listą przywróconych plików i błędów.

Jeśli lista backupów jest pusta – zwraca:

```json
{"status": "error", "msg": "Brak backupow do przywrocenia", "restored": []}
```

W takiej sytuacji rollback z poziomu Jadzia nie jest możliwy – konieczne jest użycie backupów hostingu.

---

## 6. Problemy z JWT / 401 Unauthorized

Symptomy:

- Endpointy `/worker/...` zwracają `401` z treścią:
  - `"Missing or invalid Authorization header"`
  - `"Invalid or expired token"`

### 6.1. Weryfikacja konfiguracji

1. Sprawdź, czy na VPS ustawiono `JWT_SECRET` (w `.env`):

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115
cd /root/jadzia
grep JWT_SECRET .env
```

2. Jeśli brak – dodaj:

```bash
echo 'JWT_SECRET="<JWT_SECRET>"' >> .env
sudo systemctl restart jadzia
```

3. Wygeneruj nowy token (na maszynie z kodem Jadzia):

```bash
cd /ścieżka/do/Jadzia
export JWT_SECRET="<JWT_SECRET>"
python scripts/jwt_token.py --days 30
```

4. Użyj nowego tokena w nagłówku:

```bash
curl "http://185.243.54.115:8000/worker/health" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Uwaga: gdy `JWT_SECRET` nie jest ustawiony, `verify_worker_jwt` pomija uwierzytelnianie – na produkcji powinno być zawsze ustawione.

---

## 7. Alerty Discord – brak powiadomień

Symptomy:

- Brak powiadomień na Discordzie przy błędach (`task_failed`, `rollback_failed`).

### 7.1. Weryfikacja konfiguracji

Na VPS:

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115
cd /root/jadzia
grep DISCORD_WEBHOOK_URL .env
```

Jeśli brak:

```bash
echo 'DISCORD_WEBHOOK_URL="<DISCORD_WEBHOOK_URL>"' >> .env
sudo systemctl restart jadzia
```

### 7.2. Sprawdzenie logów błędów wysyłki

`agent.alerts` loguje wyjątki przy wysyłce webhooka:

```bash
tail -100 logs/jadzia-error.log | grep "Discord alert failed"
```

Jeśli widzisz błędy:

- Zweryfikuj URL webhooka na Discordzie.
- Sprawdź, czy VPS ma dostęp do Internetu (firewall).

---

## 8. Recovery SQLite state – powrót do Phase 4

Pełna procedura w `docs/PHASE5_ROLLBACK.md`. Streszczenie:

1. Ustaw `USE_SQLITE_STATE=0` w `.env` (lub usuń tę zmienną).
2. Odtwórz JSON session files z backupu:

```bash
cd /root/jadzia
python scripts/backup_sessions_json.py           # przed Phase 5
python scripts/restore_sessions_from_backup.py <YYYY-MM-DD>
```

3. Zrestartuj aplikację:

```bash
sudo systemctl restart jadzia
```

Po rollbacku stan będzie czytany z `data/sessions/*.json`; SQLite przestaje być źródłem prawdy dla stanu sesji.

---

## 9. Szybki checklista po awarii

1. **Czy API działa?**
   - `curl http://185.243.54.115:8000/worker/health`
2. **Czy sklep odpowiada?**
   - `curl http://185.243.54.115:8000/health`
3. **Czy zadania nie wiszą?**
   - `curl http://185.243.54.115:8000/worker/dashboard -H "Authorization: Bearer <JWT_TOKEN>"`
4. **Czy logi nie zawierają świeżych wyjątków?**
   - `tail -100 /root/jadzia/logs/jadzia-error.log`
5. **Czy są alerty Discord?**
   - Sprawdź kanał; jeśli nie ma – zweryfikuj `DISCORD_WEBHOOK_URL`.

