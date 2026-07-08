# Jadzia Operator Playbook

**Audience:** Dowódca (Norbert)  
**Updated:** 2026-07-08  
**VPS:** 185.243.54.115 — `/opt/jadzia`, port 8000 (localhost or SSH tunnel)

---

## 1. Czym jest Jadzia (a czym nie jest)

| System | Rola | Jak się z nim kontaktujesz |
|--------|------|----------------------------|
| **Jadzia COI** | Operacje biznesu: zamówienia, leady, GA4, kalendarz, WP SSH | **Telegram** (primary), Worker API, skrypty VPS |
| **Design Agent INSPIRE** | Mockupy voertuigreclame na zzpackage | Wizard UI → `/api/v1/design-agent/*` (osobny produkt) |
| **Agent OS Mission Control** | Orkiestracja kodu multi-repo | `agent-os-ui` :3000 — **nie** panel Jadzii COI |
| **VCMS** | Governance, skan 8 repo | flex-vcms — dokumentacja, nie runtime Jadzii |

**Panel WWW Jadzii dziś:** brak. Metryki: `GET /worker/dashboard` (JSON + JWT).

---

## 2. Telegram — codzienna obsługa

### Komendy

| Komenda | Działanie |
|---------|-----------|
| `/pomoc` | Lista komend i HITL |
| `/zadanie <treść>` | Nowe zadanie WP (plan → diff → zatwierdzenie) |
| `/status` | Stan bieżącej operacji |
| `/cofnij` | Rollback ostatnich zmian SSH |
| `tak` / `nie` | Zatwierdź / odrzuć diff (przyciski lub tekst) |

### Bezpieczny pierwszy kontakt

1. Zacznij od `/pomoc` i `/status`
2. Pierwsze `/zadanie` — drobna zmiana; przy diffie wybierz **Nie** jeśli nie jesteś pewien
3. Produkcja WP: każdy zapis pliku wymaga Twojego **Tak**

---

## 3. Worker API i skrypty (VPS)

### JWT (lokalnie na VPS)

```bash
cd /opt/jadzia
./venv/bin/python3 scripts/jwt_token.py
```

### Wyślij zadanie (bez Telegrama)

```bash
# Bezpieczny test — bez zapisu na WP:
./venv/bin/python3 scripts/send_task.py \
  "Pokaz status systemu bez zmian w plikach" \
  --test_mode --dry_run --poll

# Kolejka bez czekania:
./venv/bin/python3 scripts/send_task.py "Twoje polecenie" --test_mode
```

### Tygodniowy brief (ręcznie)

```bash
./venv/bin/python3 -c "from agent.nodes.brief_node import send_weekly_brief; print(send_weekly_brief())"
```

Oczekiwany wynik: `True` + wiadomość na Telegram.

---

## 4. COI API (read-mostly, JWT wymagany w prod)

Z PC przez tunel SSH:

```bash
ssh -L 8000:127.0.0.1:8000 -i ~/.ssh/cyberfolks_key root@185.243.54.115
```

Następnie (z tokenem JWT):

```bash
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/worker/dashboard
curl -H "Authorization: Bearer <TOKEN>" "http://localhost:8000/api/v1/analytics/snapshot?period=7d"
curl -H "Authorization: Bearer <TOKEN>" http://localhost:8000/api/v1/content-calendar
```

**Uwaga:** `POST /chat` bez JWT → **401** w `JADZIA_ENV=production`.

---

## 5. CLI `jadzia` (5 komend)

```bash
jadzia health --url http://185.243.54.115:8000   # jeśli port publiczny
jadzia test --url http://localhost:8000          # przez tunel
jadzia status
jadzia version
jadzia urls
```

---

## 6. Ćwiczenia (Faza 4)

### E1 — Safe path (automated PASS 2026-07-08)

```bash
./venv/bin/python3 scripts/send_task.py \
  "Pokaz status systemu bez zmian w plikach" \
  --test_mode --dry_run --poll
```

**DoD:** ostatnia linia `status=completed`

### E2 — Telegram HITL (Dowódca)

1. `/zadanie Dodaj komentarz /* jadzia-test */ na końcu pliku style.css w child theme`
2. Poczekaj na diff
3. Odpowiedz **Nie** lub przycisk Odrzuć

**DoD:** brak zapisu na WP; status operacji anulowany / bez write

### E3 — Rollback (opcjonalne)

Po świadomym teście z zapisem: `/cofnij` w Telegramie lub `POST /rollback` z JWT.

---

## 7. Smoke i dowody

```bash
bash /opt/jadzia/deployment/prod-smoke.sh
bash /opt/jadzia/deployment/spine-proof-run.sh
```

Macierz: [`JADZIA-SPINE-PROOF-MATRIX.md`](JADZIA-SPINE-PROOF-MATRIX.md)

---

## 8. FAQ

**Gdzie jest panel sterowania?**  
JSON API `/worker/dashboard`. Mission Control to Agent OS, nie Jadzia COI.

**Czy mogę deployować z agenta?**  
Nie (Zasada 11). Tylko Ty, manual.

**S1-01 rotacja sekretów?**  
Osobna sesja: `docs/handoffs/2026-07-03-s1-01-secret-rotation-checklist.md`

**Design Agent wyłączyć?**  
`FG_DESIGN_AGENT_API_ENABLED=false` w wp-config.php
