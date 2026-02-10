# Weryfikacja ROADMAP_FIX – co zrobione, co zostało

**Data weryfikacji:** 2026-02-10  
**Źródła:** ROADMAP_FIX.md, SYSTEM_BIBLE.md, stan kodu (interfaces/telegram_api.py, agent/db.py, interfaces/api.py)

---

## Podsumowanie

| Faza | Task | Status | Uwagi |
|------|------|--------|--------|
| 0 | 0.1–0.3 Diagnostyka | — | Zadania ręczne (zrzut DB, logi, test SSH) |
| 1 | 1.1 Usuń in-memory cache | ❌ **NIE** | `_telegram_chat_to_task_id` nadal używany |
| 1 | 1.1b `db_get_active_task` w db.py | ❌ **NIE** | Brak funkcji; jest tylko `db_get_last_active_task` |
| 1 | 1.2 Jeden sposób task_id (tylko DB) | ❌ **NIE** | `_get_task_id_for_chat` używa cache + `get_active_task_id` (state) |
| 1 | 1.3 Structured logging | ❌ **NIE** | Brak `logger.info("[Telegram] … started", extra={...})` na wejściu |
| 1 | 1.4 Retry SSH | ✅ Obecne | `ssh_orchestrator.py` używa `@with_retry` (read_file, write_file) |
| 2 | 2.1 Połączyć callback + approval | ❌ **NIE** | Dwie osobne gałęzie: `callback` i `approval` |
| 2 | 2.2 Uproszczenie statusów | ⏸ Opcjonalne | Nie wdrożone (mapowanie wewnętrzne zostaje) |
| 2 | 2.3 Health check | ✅ Częściowo | `/health`, `/worker/health` – DB, SSH, sqlite_connection; brak jawnych: token Telegram, worker loop status |
| 3 | 3.1 Martwy kod / TODO | ✅ Brak TODO | Grep `# TODO` w *.py – brak wyników |
| 3 | 3.2 .env.example | ❌ **NIE** | Plik nie istnieje |
| 3 | 3.3 Dokumentacja deployment | ⚠ Częściowo | docs/ (RUNBOOK, OPERATIONS, RECOVERY) – brak głównego README z Wymagania/Instalacja/Konfiguracja/Troubleshooting |

---

## Szczegóły weryfikacji

### Faza 1: Stabilizacja

**Task 1.1 / 1.1b**  
- W `interfaces/telegram_api.py`: słownik `_telegram_chat_to_task_id` (lin. 46) oraz zapisy/odczyty (m.in. 82, 86, 91, 368, 382, 468, 489).  
- W `agent/db.py` **nie ma** `db_get_active_task(chat_id, source) -> Optional[str]` zwracającego `active_task_id` z tabeli `sessions`.  
- Jest: `db_get_last_active_task`, `db_get_awaiting_approval_task`, `db_get_task(task_id)`.

**Task 1.2**  
- `_get_task_id_for_chat` (lin. 69–95): najpierw cache `_telegram_chat_to_task_id`, potem `get_active_task_id(chat_id, "telegram")` z `agent.state` (który czyta load_state/JSON lub SQLite przez state).  
- Roadmap wymaga: **tylko DB** – `db_get_active_task` + fallback `db_get_last_active_task`, z weryfikacją `db_get_task(task_id)`.

**Task 1.3**  
- Brak na początku ścieżek logów w stylu:  
  `logger.info("[Telegram] %s started", func_name, extra={"task_id": ..., "chat_id": ..., "command": ...})`.

**Task 1.4**  
- W `agent/tools/ssh_orchestrator.py`: `read_file`, `write_file` itd. z `@with_retry` – OK. Roadmap: „sprawdź czy działa” – uznane za spełnione.

---

### Faza 2: Uproszczenie

**Task 2.1**  
- Callback (przyciski): osobny blok `if command == "callback"` → `submit_input(task_id, ..., approval=approval)`.  
- Approval (tekst tak/nie): osobny blok `if command == "approval"` → ta sama logika, ale inna ścieżka zdobywania `task_id`.  
- Nie ma wspólnej funkcji `_handle_approval(chat_id, task_id, approved)` wywoływanej z obu miejsc.

**Task 2.3**  
- `GET /worker/health`: zwraca `ssh_connection`, `sqlite_connection`, `active_sessions`, `queue_length`, `status` (healthy/degraded).  
- Brak: jawna informacja „worker loop działa” (np. flaga z startup), opcjonalna walidacja tokena Telegram.

---

### Faza 3: Czyszczenie

**Task 3.2**  
- `.env.example` nie istnieje w repo.

**Task 3.3**  
- W `docs/` jest RUNBOOK, OPERATIONS, RECOVERY itd.  
- W katalogu głównym brak pliku README.md z sekcjami: Wymagania, Instalacja, Konfiguracja (.env), Troubleshooting.

---

## Zgodność z SYSTEM_BIBLE

- **Źródło prawdy task_id:** SYSTEM_BIBLE mówi „SQLite – sessions i tasks”; „ZAKAZANE: in-memory dict”. Obecny kod nadal łamie to (cache w telegram_api).  
- **Logowanie:** wymagane konteksty (task_id, chat_id, status) – częściowo (np. approval ma logi), brak ujednoliconego „started” na wejściu (Task 1.3).  
- Reszta (backup, atomowość, timeout SSH) nie była przedmiotem tej weryfikacji.

---

## Rekomendowany plan działania

Priorytet: **Faza 1** (stabilizacja i jedno źródło prawdy), potem **Faza 2** (uproszczenie approval), na końcu **Faza 3** (dokumentacja i .env).

1. **Task 1.1b** – W `agent/db.py` dodać `db_get_active_task(chat_id, source) -> Optional[str]` (SELECT active_task_id FROM sessions WHERE chat_id=? AND source=?).
2. **Task 1.1 + 1.2** – W `interfaces/telegram_api.py`:  
   - Usunąć `_telegram_chat_to_task_id` i wszystkie odwołania.  
   - Zastąpić `_get_task_id_for_chat` wersją tylko z DB: `db_get_active_task` → weryfikacja `db_get_task(task_id)` → fallback `db_get_last_active_task`.
3. **Testy** – Zaktualizować `tests/test_reliability_regression.py`: testy które teraz używają `_telegram_chat_to_task_id` muszą opierać się na DB/mocku `db_get_active_task`/`db_get_last_active_task`.
4. **Task 1.3** – Dodać structured logging na wejściu do kluczowych ścieżek (np. webhook wejście, callback, approval, zadanie) z `extra={"task_id", "chat_id", "command"}`.
5. **Task 2.1** – Wydzielić `async def _handle_approval(chat_id, task_id, approved)` i wywołać ją z gałęzi `callback` (gdy mamy task_id z callback_data) oraz z gałęzi `approval` (gdy task_id z _get_task_id_for_chat / get_awaiting_approval_task_id / db_get_last_active_task).
6. **Task 2.3 (opcjonalnie)** – Rozszerzyć `/worker/health` o pole np. `worker_loop_started: true` (ustawiane w startup) i ewentualnie krótką walidację Telegram tokena (bez pełnego getMe w każdej odpowiedzi).
7. **Task 3.2** – Utworzyć `.env.example` według listy z ROADMAP_FIX.
8. **Task 3.3** – Dodać `README.md` w katalogu głównym z sekcjami: Wymagania, Instalacja, Konfiguracja (.env), Troubleshooting (z odwołaniami do docs/).

Kolejność 1→2→3 (w obrębie Fazy 1) jest ważna: najpierw DB API, potem usunięcie cache i jedna ścieżka task_id, na końcu testy i logowanie. Task 2.1 można zrobić zaraz po 1.3 (mniej ryzyka regresji po usunięciu cache).
