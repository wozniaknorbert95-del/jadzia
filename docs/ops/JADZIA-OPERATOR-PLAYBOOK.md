# Jadzia COI — Operator Playbook (Dowódca)

**Version:** 1.0 · **2026-07-08**  
**Audience:** Norbert Wozniak (Commander)  
**Prerequisite:** Spine proof matrix PASS (`JADZIA-SPINE-PROOF-MATRIX.md`)

---

## 1. Czym Jadzia jest (30 sekund)

**Jadzia COI** = operacyjny mózg FlexGrafik na VPS — nie chatbot marki, nie Design Agent.

| Kanał | Do czego |
|-------|----------|
| **Telegram** | Codzienne zadania WP (SSH, HITL, rollback) |
| **Worker API** | To samo programowo (`scripts/send_task.py`) |
| **Widget chat** | Sprzedaż Wizard/portal (INT-001) — osobny agent |
| **Webhooks/API** | Zamówienia, leady, analytics, kalendarz |
| **Panel WWW** | **Brak w jadzia-core** — tylko `GET /worker/dashboard` (JSON). Mission Control = Agent OS (`agent-os-ui`), inny produkt |

---

## 2. Telegram — komendy

| Komenda | Działanie |
|---------|-----------|
| `/pomoc` | Lista komend |
| `/zadanie <treść>` | Nowe zadanie WP (plan → diff → approval) |
| `/status` | Stan bieżącej operacji |
| `/cofnij` | Rollback ostatnich zmian SSH |
| `tak` / `nie` (lub przyciski) | Zatwierdzenie diffu (HITL) |

**Bezpieczny start:** pierwsze zadanie = komentarz CSS, nie struktura motywu.

Przykład:
```
/zadanie Dodaj komentarz /* jadzia-test */ na końcu pliku style.css w child theme
```

---

## 3. VPS — zadanie bez Telegrama

Na VPS jako root lub przez SSH:

```bash
cd /opt/jadzia

# Suchy bieg — bez zapisu na WP
./venv/bin/python3 scripts/send_task.py \
  "Dodaj komentarz /* spine-test */ w style.css" \
  --test_mode --dry_run --poll

# Status usługi
systemctl status jadzia
bash deployment/prod-smoke.sh
```

JWT (lokalnie z `.env` na VPS):
```bash
./venv/bin/python3 scripts/jwt_token.py
curl -sS -H "Authorization: Bearer $(./venv/bin/python3 scripts/jwt_token.py)" \
  http://127.0.0.1:8000/worker/dashboard | python3 -m json.tool
```

Z PC (jeśli port 8000 nie jest publiczny): SSH tunnel  
`ssh -L 8000:127.0.0.1:8000 root@185.243.54.115` → potem `http://localhost:8000`

---

## 4. COI API — mapa (JWT unless noted)

| Endpoint | Cel |
|----------|-----|
| `GET /worker/health` | SSH, queue, SQLite (no JWT) |
| `GET /worker/dashboard` | Metryki zadań |
| `POST /worker/task` | Nowe zadanie (jak Telegram) |
| `GET /api/v1/analytics/snapshot?period=7d` | GA4 |
| `GET /api/v1/content-calendar` | Kalendarz treści |
| `POST /api/v1/content-calendar` | Nowy wpis |
| `GET /costs` | Koszty tokenów |
| `GET /sessions` | Aktywne sesje |
| `POST /api/v1/widget/chat` | Chat sprzedażowy (bez JWT) |
| `POST /webhooks/woocommerce/order` | WC (HMAC, nie ręcznie) |
| `POST /api/v1/leads` | Leady z app (API key) |

CLI (z PC, jeśli API reachable):
```bash
python -m cli.main health --url http://185.243.54.115:8000
python -m cli.main test --url http://185.243.54.115:8000
```

---

## 5. Trzy ćwiczenia (zrób sam — checkbox)

### Ćwiczenie A — Safe dry run
1. VPS: `send_task.py` z `--test_mode --dry_run --poll`
2. **Done gdy:** status `completed` bez zmiany plików na WP

### Ćwiczenie B — Telegram HITL
1. `/zadanie` — drobna zmiana CSS (komentarz)
2. `/status` — czekaj na `diff_ready`
3. `nie` — odrzuć diff
4. **Done gdy:** brak write na produkcji

### Ćwiczenie C — COI read-only
1. JWT + `GET /worker/dashboard`
2. `GET /api/v1/analytics/snapshot?period=7d`
3. `sqlite3 data/jadzia.db "SELECT COUNT(*) FROM orders; SELECT COUNT(*) FROM leads;"`
4. **Done gdy:** widzisz liczby bez błędu 401

Zaznacz w handoff: `docs/handoffs/2026-07-08-jadzia-spine-closure-complete.md`

---

## 6. Weekly brief

Skonfigurowane: `WEEKLY_BRIEF_INTERVAL_SECONDS=604800` (7 dni).

Ręczny trigger (VPS):
```bash
cd /opt/jadzia && ./venv/bin/python3 -c \
  "from agent.nodes.brief_node import send_weekly_brief; print(send_weekly_brief())"
```

Sprawdź Telegram Dowódcy.

---

## 7. Rollback i awarie

| Problem | Akcja |
|---------|-------|
| Zła zmiana WP | `/cofnij` w Telegram lub `POST /rollback` (JWT) |
| Service down | `systemctl restart jadzia` · logi: `/opt/jadzia/logs/` |
| Smoke fail | `docs/ops/PLAN-DEPLOY-CLOSURE-2026-07-05.md` |
| Design Agent off | `FG_DESIGN_AGENT_API_ENABLED=false` w wp-config |

---

## 8. Czego nie robić

- Nie deployuj sam bez checklisty (Zasada 11)
- Nie testuj FB publish bez świadomej decyzji (live post)
- Nie używaj `Desktop\o systemie.txt` — SSoT: `brain.md` + ten playbook
- S1-01 rotacja sekretów — osobna sesja: `docs/handoffs/2026-07-03-s1-01-secret-rotation-checklist.md`

---

## 9. Następny poziom (po ćwiczeniach)

- Edge hardening: `docs/ops/VPS-EDGE-HARDENING.md`
- B3.1 FB sense (deferred w todo)
- Agent OS Mission Control — osobny stack
