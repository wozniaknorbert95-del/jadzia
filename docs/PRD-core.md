# PRD-core.md — jadzia-core
*Wersja: 1.0 | Projekt: Jadzia AI Agent | Właściciel: Norbert Woźniak*

---

## OPIS PROJEKTU

Jadzia — agent AI zarządzający ekosystemem FlexGrafik.
Core: edycja plików WordPress przez SSH na podstawie komend Telegram.
Rozbudowa: pełny silnik operacyjny (onboarding, produkcja, logistyka, marketing).

VPS: 185.243.54.115 (Ubuntu 24.04, 7.8GB RAM, 98GB SSD)
Tech: Python, FastAPI, LangGraph, SQLite, Telegram Bot, Claude API
Service: sudo systemctl restart jadzia
Logi: /root/jadzia/logs/jadzia-error.log
DB: /root/jadzia/data/jadzia.db

---

## TECH STACK

- Python 3.12
- FastAPI + LangGraph
- SQLite (jadzia.db)
- Telegram Bot API
- Claude Haiku 4 (routing, proste zadania)
- Claude Sonnet 4.5 (planowanie, generowanie kodu)
- Paramiko (SSH do Cyber-Folks)
- rclone (backup → Google Drive)

---

## PIPELINE (CORE — DZIAŁA)

```
queued → planning → reading_files → generating_code
→ diff_ready [Tak/Nie od Norberta]
→ writing_files → completed / rolled_back
```

Komendy Telegram: /zadanie, /status, /cofnij, /pomoc, Tak, Nie

---

## FEATURE LIST

### CORE (działa)
| Feature | Status |
|---------|--------|
| Routing Haiku | ✅ Działa |
| Planning Sonnet | ✅ Działa |
| Generator kodu | ✅ Działa |
| SSH executor (Paramiko) | ✅ Działa |
| Backup przed zapisem | ✅ Działa |
| Human-in-the-loop (Tak/Nie) | ✅ Działa |
| Telegram bot komendy | ✅ Działa |
| Rollback przy błędzie | ✅ Działa |

### NODY OPERACYJNE (do zbudowania — po domenach)
| Node | Status | Priorytet |
|------|--------|-----------|
| onboarding_node.py | 🔴 Planned | 1 |
| production_node.py | 🔴 Planned | 2 |
| postnl_node.py | 🔴 Planned | 3 |
| installer_node.py | 🔴 Planned | 4 |

### AGENTY SPECJALISTYCZNE (do zbudowania — po nodach)
| Agent | Status | Priorytet |
|-------|--------|-----------|
| Content Engine | 🔴 Planned | 1 |
| Lead Scout | 🔴 Planned | 2 |
| Game Master | 🔴 Planned | 3 |

### INFRASTRUKTURA (do zbudowania)
| Feature | Status | Priorytet |
|---------|--------|-----------|
| Webhook WooCommerce → jadzia.db | ⏳ Q1 2026 | KRYTYCZNY |
| Admin Dashboard | 🔴 Planned | WYSOKI |
| Endpoint /costs monitoring | ✅ Działa | — |
| Endpoint /health | ✅ Działa | — |

---

## DEPLOY CONFIG

```
VPS: 185.243.54.115
User: root
Service: jadzia.service
Deploy flow:
  1. TS=$(date +%Y%m%d-%H%M%S)
  2. sqlite3 /root/jadzia/data/jadzia.db ".backup /root/jadzia/backups/pre-deploy-$TS.db"
  3. git pull origin main
  4. pip install -r requirements.txt
  5. alembic upgrade head
  6. systemctl restart jadzia.service
  7. sleep 3 && curl -f localhost:8000/health
  FAIL? → alembic downgrade -1 → git checkout HEAD~1 → restore backup → restart
```

Cron backup 2AM: rclone sync /data/ gdrive:jadzia-backup

---

## AI GUIDELINES

- Schema change → PRD-schema.md update NAJPIERW, alembic migration RAZEM z kodem
- Feature branch only, nigdy main
- Backup DB przed każdą zmianą schema
- pytest po każdej zmianie w app/
- Jeden node na raz — nie buduj wszystkich równolegle
- Domeny muszą być gotowe PRZED rozbudową nodów
- NIE modyfikuj plików poza app/[twój-scope]/
