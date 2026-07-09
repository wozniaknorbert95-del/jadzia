# Handoff PROOF: COI Commander v3 — prod deploy (2026-07-09)

**Branch:** `feat/design-agent-inspire-v2`  
**Commit:** `1706b6a50d3d13c6f83d441ce63dbbd8e066d9c2`  
**Gate:** `COI-CMD-DEPLOY-01` → **completed**  
**VPS:** `185.243.54.115` `/opt/jadzia` (branch `feat/design-agent-inspire-v2` @ `1706b6a`)  
**Public URL:** https://api.zzpackage.flexgrafik.nl/commander/

---

## Git

| Krok | Status |
|------|--------|
| Commit Commander (bez INSPIRE engine) | ✅ `1706b6a` |
| Push `origin/feat/design-agent-inspire-v2` | ✅ |
| INSPIRE `agent/inspire/engine.py` | ⏸ unstaged lokalnie — osobny commit |

---

## VPS deploy

| Krok | Status | Uwaga |
|------|--------|-------|
| DB backup | ✅ `jadzia.db.bak.20260709*` | |
| `git stash` lokalnych zmian VPS | ✅ `pre-coi-commander-deploy-20260709` | |
| Checkout `feat/design-agent-inspire-v2` | ✅ | VPS był na `master` |
| `pip install -r requirements.txt` | ✅ | |
| `systemctl restart jadzia` | ✅ active | |
| Nginx `/commander` | ✅ via `location /` → :8000 | Osobny blok nie wymagany |

---

## Prod smoke (po deploy)

**Script:** `deployment/commander-prod-smoke.sh` — **7/7 PASS**

| Test | Wynik |
|------|-------|
| `GET /commander/` localhost | 200 |
| `GET /commander/` public HTTPS | 200 |
| `GET /api/v1/commander/queue` + JWT `role:dowodca` | 200 |
| `GET /api/v1/agents` | 200 |
| `POST /api/v1/commander/tickets` + deeplink | 200 |
| CRITICAL wpis w queue | ✅ |
| `PATCH settings` → `delegat_email` | ✅ `delegat@flexgrafik.nl` |

**TG `/ticket test`** — ⚠️ **nie testowane live** w tej sesji (wymaga ręcznego `/ticket` w bocie). API ticket + deeplink potwierdzone.

---

## Testy lokalne (po deploy)

```
pytest tests/unit/test_commander_api.py \
       tests/unit/test_content_calendar_api.py \
       tests/unit/test_auth_hardening.py -q
→ 27 passed
```

---

## Znane luki (backlog — nie blokują)

| ID | Opis |
|----|------|
| COI-CMD-GAP-N16 | TG push gdy dashboard down >5 min |
| COI-CMD-GAP-UNDO60 | CE-05 60s internal undo w UI |
| COI-CMD-WORKSHOP | F0 workshop + test no-laptop (Dowódca) |
| Email Delegata | Tylko zapis w settings + TG escalation worker |

---

## Następny krok

1. **Ty:** wyślij TG `/ticket test opis` — potwierdź signed link na telefonie
2. **Ty:** otwórz https://api.zzpackage.flexgrafik.nl/commander/ — wklej JWT, sprawdź queue
3. **Agent:** merge `feat/design-agent-inspire-v2` → `master` gdy Dowódca approve
4. **Agent:** N16 + undo60 w osobnych sesjach
