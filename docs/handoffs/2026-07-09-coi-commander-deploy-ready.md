# Handoff: COI Commander v3 — deploy-ready (2026-07-09)

**Branch:** `feat/design-agent-inspire-v2`  
**Gate:** Deploy **NIE wykonany** (Zasada 11) — następna sesja `@jadzia-deploy`  
**Plan:** `docs/design/coi-commander/COI-COMMANDER-PLAN-v3.md`

---

## Co zrobiono (sesja)

### F0 — Spec (D0.1–D0.14)
- `docs/design/coi-commander/UX-BRIEF-COMMANDER.md`
- Specy: `specs/D0.7` … `D0.14`, `adr/D0.5-hosting-adr.md`
- `WORKSHOP-F0-CHECKLIST.md`, `T1-T13-VERIFICATION.md`, `AUDYT-V2-GAP.md`

### F1 — Backend control plane
- `agent/commander/` — queue, audit (hash-chain), authz, SLA, graduation, agents, deeplink, publish/unpublish, escalation, tickets, settings
- `api/routes/commander.py` — pełny zestaw endpointów planu v3
- `api/dependencies.py` — `require_scope()` server-side (N7)
- `agent/db.py` — tabele commander_* + `version` na content_calendar
- `api/telegram.py` — `/zadanie` → `/ticket` + signed deep-link (CE-02, zero SSH z TG)
- Worker hook: `check_sla_escalations()` w pętli FB publish

### F2 — MVP UI
- `commander-ui/` — Home, Marketing, Analytics, Agents, Settings (PL)
- Mount: `/commander/` w `api/app.py`

### F3 / F3.1 (MVP)
- Registry agentów + pause/resume + held queue
- Graduation via `POST /feedback`
- Settings: delegat_email, ui_language

### Testy lokalne (PASS)
```
pytest tests/unit/test_commander_api.py \
       tests/unit/test_content_calendar_api.py \
       tests/unit/test_auth_hardening.py -q
→ 27 passed
```

---

## Weryfikacja deploy-ready

| Kryterium | Status | Uwaga |
|-----------|--------|-------|
| CE-01 tiered queue | ✅ | API + UI |
| CE-02 no SSH z TG | ✅ | `/ticket` only |
| CE-03 SLA escalation | 🟡 | TG push w worker; brak email do Delegata |
| CE-05 unpublish public | ✅ | API + UI confirm |
| CE-05 60s internal undo | 🟡 | Spec only — brak timera w UI |
| CE-07 ApprovalCard context | 🟡 | Queue item ma pola; nie pełny komponent |
| CE-09 authz server-side | ✅ | 403 viewer na pause |
| CE-10 freshness | ✅ | Analytics tiles + API |
| N1 no-laptop deeplink | ✅ | Kod gotowy; **brak prod testu** |
| N16 dashboard-down TG | ❌ | Nie zaimplementowane |
| Commit | ❌ | Zmiany **uncommitted** |
| Prod deploy | ❌ | Do następnej sesji |

---

## Pliki zmienione (git status)

```
M  agent/db.py
M  agent/inspire/engine.py   ← UWAGA: osobna zmiana INSPIRE — sprawdź przed commitem
M  api/app.py
M  api/dependencies.py
M  api/telegram.py
?? agent/commander/
?? api/routes/commander.py
?? commander-ui/
?? docs/AUDYT-HIL-KONTROLA.md
?? docs/design/coi-commander/
?? tests/unit/test_commander_api.py
```

**HEAD:** `c91a3f1` (spine closure docs) — Commander **nie jest w commicie**.

---

## Deploy checklist (następna sesja — Dowódca)

1. **Review diff** — rozdziel commit Commander vs `agent/inspire/engine.py` jeśli potrzeba
2. **Commit** wszystkich plików COI Commander (+ docs)
3. **Push** branch → merge strategy (main lub deploy z feature branch)
4. **VPS** (`/opt/jadzia`, `185.243.54.115`):
   - `git pull` / deploy script
   - `systemctl restart jadzia`
   - SQLite migracja automatyczna przy starcie (`commander_*` tabele)
5. **Nginx** (jeśli brak): `location /commander` → proxy do :8000 lub static
6. **JWT** z claim `role: dowodca` dla operatora
7. **Smoke prod:**
   - `GET https://<host>/commander/` → 200 HTML
   - `GET /api/v1/commander/queue` + Bearer → 200
   - `GET /api/v1/agents` → lista agentów
   - TG `/ticket test opis` → link signed + queue CRITICAL
8. **Settings:** ustaw `delegat_email` w Commander UI
9. **Opcjonalnie:** test no-laptop (telefon + signed link)

Skrypt bazowy: `deployment/deploy-to-vps.sh` + `deployment/prod-smoke.sh`

---

## Co zostaje (post-deploy / Faza C)

- N16: TG push gdy dashboard down >5 min
- 60s soft-undo timer w UI (internal actions)
- Email escalation do Delegata (obecnie tylko TG + zapis email w settings)
- F0 workshop live z Dowódcą (checklist gotowy)
- Scorecard 6 wymiarów na prod
- S1-01 secret rotation (deferred)
- Moduły Phase C placeholders (Procurement, Finance, …)

---

## Ryzyka

- **Uncommitted** — deploy bez commitu = chaos na VPS
- **inspire/engine.py** w tym samym working tree — ryzyko przypadkowego mix w commicie
- **JWT bez `role`** — domyślnie `dowodca` (backward compat) — OK dla Norberta, źle jeśli wielu userów
- **Nginx /commander** — może nie być skonfigurowane na prod
- **Brak prod proof** — lokalne testy only

---

## Referencje

- Plan: `docs/design/coi-commander/COI-COMMANDER-PLAN-v3.md`
- README: `docs/design/coi-commander/README.md`
- Audyt: `docs/AUDYT-HIL-KONTROLA.md`, `docs/design/coi-commander/AUDYT-V2-GAP.md`
