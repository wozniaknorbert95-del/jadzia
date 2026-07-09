# Handoff PROOF: COI Commander v3 — merge master + prod deploy (2026-07-09)

**Gate:** `COI-CMD-MERGE-DONE`  
**Branch:** `master` @ `f24cf5e`  
**Merge:** `feat/design-agent-inspire-v2` → `master` (fast-forward)  
**VPS:** `185.243.54.115` `/opt/jadzia`  
**Public URL:** https://api.zzpackage.flexgrafik.nl/commander/

---

## Git

| Krok | Status |
|------|--------|
| `git checkout master && git pull` | ✅ `0f52d10` |
| Merge `feat/design-agent-inspire-v2` | ✅ fast-forward → `f24cf5e` |
| `git push origin master` | ✅ |
| INSPIRE WIP (`engine.py` safety retry) | ⏸ `git stash` na feature branch |

---

## VPS deploy (master)

| Krok | Status |
|------|--------|
| `git checkout master && git pull` | ✅ |
| `systemctl restart jadzia` | ✅ active |
| `deployment/commander-prod-smoke.sh` | ✅ see below |

---

## Prod smoke

**Script:** `deployment/commander-prod-smoke.sh` — **10/10 PASS** @ `f24cf5e`

| Test | Wynik |
|------|-------|
| GET /commander/ local + public | 200 |
| queue, agents, tickets, CRITICAL queue | OK |
| PATCH settings delegat_email | OK |
| GET graduation, audit-log | OK |
| delegat cannot pause | 403 |

---

## Testy lokalne (master)

```bash
pytest tests/unit/test_commander_*.py tests/unit/test_content_calendar_api.py -q
→ 29 passed
```

---

## Twoja kolej (Dowódca)

1. Wygeneruj JWT: `python scripts/jwt_token.py --role dowodca --sub norbert` (na VPS z `.env`)
2. Otwórz https://api.zzpackage.flexgrafik.nl/commander/ → wklej token
3. TG: `/ticket test workshop` → klik link na **telefonie**
4. Ustawienia → email Delegata → Zapisz
5. Zaznacz workshop checklist po testach

---

## Backlog

- INSPIRE engine stash — osobny commit po `git stash pop` na feature branch
- F4 Paid ads — Phase C placeholder only
- Workshop test #2 (3d offline delegat) — czasowy, nie blokuje
