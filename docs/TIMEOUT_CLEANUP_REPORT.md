# TIMEOUT CLEANUP – analiza i fix

## Kontekst z logów

```
[FAILED_SET] reason=worker_awaiting_timeout: threshold=30min
```

Zadanie w stanie „czeka na odpowiedź użytkownika” (planning + awaiting_response lub diff_ready + awaiting_response) było oznaczane jako FAILED po 30 minutach i usuwane z kolejki.

---

## 1. Gdzie jest timeout

**Plik:** `interfaces/api.py`  
**Stała (linie 718–719):**

```python
WORKER_STALE_TASK_MINUTES = int(os.getenv("WORKER_STALE_TASK_MINUTES", "15") or "15")
WORKER_AWAITING_TIMEOUT_MINUTES = int(os.getenv("WORKER_AWAITING_TIMEOUT_MINUTES", "30") or "30")
```

**Logika timeoutu „awaiting”** – w pętli worker (_worker_loop), w bloku dla aktywnego taska (linie 1012–1054). Fragment odpowiedzialny za decyzję i ustawienie FAILED:

```python
# Awaiting-timeout: only for PLANNING + awaiting_response (user never responded).
# Uses created_at for age; threshold WORKER_AWAITING_TIMEOUT_MINUTES so we don't
# block the queue indefinitely. Mark FAILED and advance; RUNNING/COMPLETED/FAILED unchanged.
if status_val == "planning" and task_dict.get("awaiting_response", False):
    awaiting_threshold = WORKER_AWAITING_TIMEOUT_MINUTES
    awaiting_timed_out = False
    aw_ts_str = (task_dict.get("created_at") or "").strip()
    aw_field_used = "created_at" if aw_ts_str else "updated_at"
    if not aw_ts_str:
        aw_ts_str = (task_dict.get("updated_at") or "").strip()
        print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: created_at missing, using updated_at")
    aw_dt = _parse_timestamp_to_utc(aw_ts_str) if aw_ts_str else None
    if aw_dt and awaiting_threshold > 0:
        aw_age_minutes = _safe_age_minutes(aw_dt)
        if aw_age_minutes > awaiting_threshold:
            awaiting_timed_out = True
        else:
            print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: using {aw_field_used} age_minutes={aw_age_minutes:.1f} threshold={awaiting_threshold} (not timed out)")
    elif not aw_ts_str:
        print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: no timestamp, cannot determine age")
    elif awaiting_threshold <= 0:
        print(f"  [worker_loop] session {source}/{chat_id} awaiting timeout check: WORKER_AWAITING_TIMEOUT_MINUTES={awaiting_threshold}, disabled")
    if awaiting_timed_out:
        reason = f"worker_awaiting_timeout: field={aw_field_used} value={aw_ts_str} threshold={awaiting_threshold}min"
        print(f"  [worker_loop] FAILED_SET task_id={active_id} chat_id={chat_id} source={source} reason={reason}")
        try:
            await asyncio.to_thread(add_error, reason, chat_id, source, active_id)
            await asyncio.to_thread(
                update_operation_status,
                OperationStatus.FAILED,
                chat_id,
                source,
                task_id=active_id,
            )
            next_task_id = await asyncio.to_thread(
                mark_task_completed, chat_id, active_id, source
            )
            print(f"  [worker_loop] session {source}/{chat_id}: awaiting timeout cleared => next_task_id={next_task_id}")
        except Exception as e:
            ...
```

Czyli: **tylko** dla `status == "planning"` **i** `awaiting_response == True` liczy się wiek od `created_at` (lub `updated_at`). Gdy `age_minutes > WORKER_AWAITING_TIMEOUT_MINUTES` (domyślnie 30), task jest oznaczany jako FAILED i usuwany z kolejki (add_error + update_operation_status(FAILED) + mark_task_completed).

---

## 2. Gdzie task jest „usuwany” po timeout

- **FAILED_SET** w logu to efekt wywołania **`update_operation_status(OperationStatus.FAILED, ...)`** w `agent/state.py` (tam jest `print` z `[FAILED_SET]`).
- **Usunięcie z kolejki** to **`mark_task_completed(chat_id, active_id, source)`** w `interfaces/api.py` (linie 1046–1048) – po timeout worker wywołuje kolejno:
  1. `add_error(reason, ...)` – dopisanie błędu do taska,
  2. `update_operation_status(OperationStatus.FAILED, ...)` – ustawienie statusu FAILED (stąd [FAILED_SET]),
  3. `mark_task_completed(...)` – posprzątanie aktywnego taska i przejście do następnego w kolejce.

Task nie jest fizycznie usuwany z bazy; jest oznaczany jako FAILED i usuwany z aktywnej kolejki (active_task_id + task_queue).

---

## 3. Opcje fixa

| Opcja | Opis | Skutek |
|-------|------|--------|
| **A** | Zwiększyć timeout z 30 min na 24 h dla tasków awaiting (planning + awaiting_response). | Użytkownik ma 24 h na odpowiedź (np. approval); po 24 h nadal FAILED + advance. |
| **B** | Nie ustawiać FAILED dla awaiting_approval, tylko „expired”. | Wymagałoby nowego statusu/flagi i innej logiki advance; bez advance kolejka by stała. |
| **C** | Timeout tylko dla tasków „bez user interaction”. | Obecna logika i tak dotyczy tylko „planning + awaiting_response” (czeka na użytkownika); można ewentualnie wyłączyć timeout tylko dla diff_ready (approval). |

Rekomendacja: **Opcja A** – zmiana domyślnego progu na 24 h (1440 min) i ewentualnie osobna stała tylko dla approval (np. diff_ready), bez zmiany modelu statusów ani kolejki.

---

## 4. Konkretny fix (Opcja A – 24 h)

Domyślny timeout awaiting zmieniony z 30 min na 24 h. Wartość nadal z env; ustawienie `WORKER_AWAITING_TIMEOUT_MINUTES=0` wyłącza timeout (brak FAILED po czasie).

### Zmiana 1 – stała i domyślna wartość

**PRZED (linie 718–719 w interfaces/api.py):**

```python
WORKER_STALE_TASK_MINUTES = int(os.getenv("WORKER_STALE_TASK_MINUTES", "15") or "15")
WORKER_AWAITING_TIMEOUT_MINUTES = int(os.getenv("WORKER_AWAITING_TIMEOUT_MINUTES", "30") or "30")
```

**PO:**

```python
WORKER_STALE_TASK_MINUTES = int(os.getenv("WORKER_STALE_TASK_MINUTES", "15") or "15")
# Awaiting user response (plan approval, answer_questions, etc.). Default 24h; set 0 to disable.
WORKER_AWAITING_TIMEOUT_MINUTES = int(os.getenv("WORKER_AWAITING_TIMEOUT_MINUTES", "1440") or "1440")
```

Żadnych innych zmian w kodzie nie potrzeba – ta stała jest już używana w powyższym fragmencie worker loopu; po deployu na VPS timeout będzie 24 h, chyba że w .env ustawisz inną wartość (np. `0` = wyłączony).

---

## 5. Opcjonalnie: wyłączenie tylko dla approval (diff_ready) – Opcja C

Jeśli chcesz, żeby **tylko** tasky w stanie „planning + awaiting” (np. plan_approval, answer_questions) miały timeout 30 min, a **diff_ready (approval Tak/Nie)** w ogóle nie były zabijane po czasie:

- Można dodać warunek: **nie** stosować awaiting-timeout, gdy `status_val == "diff_ready"` (tylko gdy `status_val == "planning"` i `awaiting_response`).
- Obecny kod **już** stosuje timeout tylko przy `status_val == "planning"`; dla `diff_ready` ten blok się nie wykonuje. Czyli jeśli w logu widzisz `worker_awaiting_timeout`, to task miał wtedy status **planning**. Jeśli chcesz mieć osobny (dłuższy) limit tylko dla „approval” (diff_ready), trzeba by dodać drugi blok dla `status_val == "diff_ready"` z osobnym progiem (np. 24 h) lub pominięciem timeoutu; to już rozbudowa względem prostej Opcji A.

---

## Podsumowanie

- **Gdzie:** `interfaces/api.py` – stała `WORKER_AWAITING_TIMEOUT_MINUTES` (domyślnie 30), używana w _worker_loop dla `planning` + `awaiting_response`.
- **Co robi timeout:** ustawia task na FAILED, dopisuje błąd, wywołuje `mark_task_completed` (advance kolejki).
- **Fix:** zmiana domyślnej wartości z `"30"` na `"1440"` (24 h) w jednej linii (jak wyżej). Na VPS można dodatkowo ustawić w .env np. `WORKER_AWAITING_TIMEOUT_MINUTES=1440` lub `0` (wyłączenie).

Raport zapisany; zmiana kodu w następnym kroku (edycja pliku).
