## Jadzia V4 – Incident Runbook

**Cel:** gotowe scenariusze „krok po kroku” dla najczęstszych incydentów w Jadzia V4. Każdy scenariusz zawiera: detekcję, działania, weryfikację i powiązane endpointy.

Powiązane dokumenty:

- `OPERATIONS.md` – opis endpointów i operacji dziennych.
- `RECOVERY.md` – szczegółowe procedury odtwarzania.
- `docs/PHASE5_ROLLBACK.md` – rollback SQLite → JSON state.

---

## 1. Incydent: Sklep nie działa / błędy HTTP w przeglądarce

### 1.1. Detekcja

- Zgłoszenie od użytkownika / monitoring HTTP sklepu.
- Strona główna sklepu (URL z `SHOP_URL`) ładuje się bardzo wolno, zwraca 5xx lub biały ekran.

### 1.2. Kroki

1. **Sprawdź health sklepu przez API Jadzia:**

```bash
curl "http://185.243.54.115:8000/health"
```

2. **Sprawdź Worker health i SSH:**

```bash
curl "http://185.243.54.115:8000/worker/health"
curl "http://185.243.54.115:8000/test-ssh"
```

3. **Jeśli `/health` zwraca `status="error"` lub `warning`:**
   - Sprawdź logi sklepu na hostingu (SSH na WordPress zgodnie z konfiguracją `SSH_HOST`, `SSH_USER`, `BASE_PATH`).
   - Jeśli problem wynika z ostatnich zmian w plikach (motyw/wtyczki) – **rozważ rollback** (sekcja 3).

4. **Jeśli problem wynika z hostingu (baza, PHP, serwer www):**
   - Eskaluj do administratora hostingu z logami błędów.

### 1.3. Weryfikacja

- Ponownie:

```bash
curl "http://185.243.54.115:8000/health"
curl "http://185.243.54.115:8000/worker/health"
```

- Ręczny test w przeglądarce sklepu.

---

## 2. Incydent: Worker API nie odpowiada / 5xx

### 2.1. Detekcja

- Integracje (Director / n8n) zgłaszają błędy przy wywołaniu `/worker/task` lub `/worker/task/{task_id}`.
- `curl http://185.243.54.115:8000/worker/health` nie odpowiada lub zwraca 5xx.

### 2.2. Kroki

1. **Przed SSH: upewnij się, że klucz istnieje (unikaj interaktywnego hasła):**

```bash
# Z repozytorium Jadzia (lokalnie lub na VPS):
./scripts/check_ssh_key.sh
# Lub jawnie: ./scripts/check_ssh_key.sh /root/.ssh/cyberfolks_key
```

   Jeśli klucz brakuje, skrypt zwróci błąd i wyjście 1. **Uprawnienia kluczy** (zalecane 600 dla kluczy prywatnych):

```bash
chmod 700 ~/.ssh
chmod 600 ~/.ssh/cyberfolks_key
# Wszystkie klucze prywatne (bez .pub): for f in ~/.ssh/*; do [ -f "$f" ] && [ "${f%.pub}" = "$f" ] && chmod 600 "$f"; done
```

2. **Zaloguj się na VPS i sprawdź serwis:**

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115
sudo systemctl status jadzia
```

3. **Sprawdź logi:**

```bash
cd /root/jadzia
tail -100 logs/jadzia.log
tail -100 logs/jadzia-error.log
```

4. **Jeśli serwis padł / wiesza się – restart:**

```bash
sudo systemctl restart jadzia
sleep 5
curl "http://localhost:8000/worker/health"
```

5. **Jeśli po restarcie nadal błędy w logach (np. baza SQLite, env):**
   - Postępuj zgodnie z sekcjami „Problemy SQLite” i „JWT / 401” w `RECOVERY.md`.

### 2.3. Weryfikacja

- `curl "http://185.243.54.115:8000/worker/health"` – oczekiwany JSON.
- Testowe zadanie:

```bash
curl -X POST "http://185.243.54.115:8000/worker/task" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "instruction": "Prosty test: wypisz listę plików motywu",
    "chat_id": "incident_test",
    "test_mode": true
  }'
```

---

## 3. Incydent: Zły deploy – trzeba cofnąć zmiany

### 3.1. Detekcja

- Po wykonaniu operacji przez Jadzia (lub manualnym deployu) sklep przestaje działać poprawnie.
- Na Discordzie pojawia się alert `"task_failed"` lub `"rollback_failed"`.

### 3.2. Kroki – rollback z poziomu Jadzia

1. **Sprawdź health sklepu:**

```bash
curl "http://185.243.54.115:8000/health"
```

2. **Wywołaj rollback:**

```bash
curl -X POST "http://185.243.54.115:8000/rollback"
```

3. **Przeanalizuj wynik:**
   - `status="ok"` – wszystkie pliki przywrócone.
   - `status="partial"` – część plików się nie przywróciła (sprawdź `errors` i logi).
   - `status="error"` / `msg="Brak backupow do przywrocenia"` – brak backupów; konieczny rollback po stronie hostingu.

4. **Jeśli rollback częściowy lub nieudany:**
   - Zbierz `restored`, `errors` i logi `logs/jadzia-error.log`.
   - Przygotuj eskalację do administratora hostingu z listą plików i błędów.

### 3.3. Weryfikacja

```bash
curl "http://185.243.54.115:8000/health"
curl "http://185.243.54.115:8000/worker/health"
```

- Test w przeglądarce sklepu.
- Sprawdzenie alertów Discord (`rollback_executed` / `rollback_failed`).

---

## 4. Incydent: Zadanie wisi / kolejka nie rusza

### 4.1. Detekcja

- `/worker/task/{task_id}` długo zwraca `status="in_progress"` lub `awaiting_input=true`.
- `/worker/dashboard` pokazuje rosnącą liczbę `in_progress` lub `error`.

### 4.2. Kroki

1. **Zidentyfikuj taski:**

```bash
curl "http://185.243.54.115:8000/worker/dashboard" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

2. **Jeśli wiesz, że zadanie nie dojdzie do skutku – oznacz je jako failed:**

```bash
curl -X POST "http://185.243.54.115:8000/worker/tasks/cleanup" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "task_ids": ["<TASK_ID>"],
    "reason": "manual_cleanup"
  }'
```

3. **Jeśli sesja jest zablokowana – awaryjne czyszczenie stanu:**

```bash
curl -X POST "http://185.243.54.115:8000/clear"
```

4. **Ponów zadanie (opcjonalnie w `test_mode=true`):**

```bash
curl -X POST "http://185.243.54.115:8000/worker/task" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "instruction": "To samo zadanie ale w test_mode",
    "chat_id": "shop_prod_1",
    "test_mode": true
  }'
```

### 4.3. Weryfikacja

- `/worker/task/{task_id}` zwraca `status="completed"` lub `status="error"` zamiast wiszącego `in_progress`.
- Nowe zadania przechodzą przez pełny flow (plan → diff → completed).

---

## 5. Incydent: Masowe błędy zadań / rosnące errors_last_24h

### 5.1. Detekcja

- `/worker/dashboard` pokazuje:
  - wysokie `errors_last_24h`,
  - rosnącą liczbę zadań `status="error"`.
- W logach i/lub na Discordzie pojawia się wiele `task_failed`.

### 5.2. Kroki

1. **Analiza dashboardu:**

```bash
curl "http://185.243.54.115:8000/worker/dashboard" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

2. **Analiza logów:**

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115
cd /root/jadzia
tail -200 logs/jadzia-error.log
```

3. **Jeśli źródłem są błędy środowiskowe (SSH, baza, env):**
   - Napraw je zgodnie z `RECOVERY.md` (sekcje o SSH, SQLite, JWT).

4. **Jeśli źródłem są błędy w logice zadań (np. jeden typ instrukcji psuje się zawsze):**
   - Tymczasowo zablokuj daną ścieżkę w integracji (np. n8n/Director).
   - Zgromadź przykładowe taski i logi do analizy developerskiej.

### 5.3. Weryfikacja

- Po naprawie:
  - nowe zadania tego typu kończą się `status="completed"` / `status="diff_ready"`.
  - trend `errors_last_24h` stabilizuje się.

---

## 6. Incydent: Problemy z JWT / nagłe 401 na Worker API

### 6.1. Detekcja

- Nagle wszystkie wywołania `/worker/...` zwracają `401`:
  - `"Missing or invalid Authorization header"`
  - `"Invalid or expired token"`

### 6.2. Kroki

1. **Sprawdź, czy `JWT_SECRET` nie został zmieniony na VPS:**

```bash
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115
cd /root/jadzia
grep JWT_SECRET .env
```

2. **Jeśli wartość się zmieniła – wygeneruj nowe tokeny:**

```bash
cd /ścieżka/do/Jadzia
export JWT_SECRET="<JWT_SECRET>"
python scripts/jwt_token.py --days 365
```

3. **Zaktualizuj konfigurację integracji (Director / n8n) o nowy `<JWT_TOKEN>`.**

4. **Jeśli `JWT_SECRET` nie jest ustawiony, a oczekujesz auth:**

```bash
echo 'JWT_SECRET="<JWT_SECRET>"' >> .env
sudo systemctl restart jadzia
```

### 6.3. Weryfikacja

```bash
curl "http://185.243.54.115:8000/worker/health" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

Oczekiwany: brak 401.

---

## 7. Szybka procedura po każdym deployu

1. **Health API i Worker:**

```bash
curl "http://185.243.54.115:8000/"
curl "http://185.243.54.115:8000/worker/health"
```

2. **Test zadania w `test_mode=true`:**

```bash
curl -X POST "http://185.243.54.115:8000/worker/task?dry_run=true" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <JWT_TOKEN>" \
  -d '{
    "instruction": "Przetestuj prostą zmianę w motywie",
    "chat_id": "post_deploy_check",
    "test_mode": true
  }'
```

3. **Sprawdzenie dashboardu:**

```bash
curl "http://185.243.54.115:8000/worker/dashboard" \
  -H "Authorization: Bearer <JWT_TOKEN>"
```

4. **Monitorowanie alertów Discord przez min. 15 minut po deployu.**

