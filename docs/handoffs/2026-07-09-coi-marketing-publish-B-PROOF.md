# Handoff PROOF: COI Marketing Publish Hardening — Phase B (2026-07-09)

**Branch:** `master` @ `1036d6e`  
**Gate:** `COI-MARKETING-PUBLISH-B` → **completed**  
**VPS:** `/opt/jadzia` @ `1036d6e` — `jadzia` active (2026-07-09)

---

## Co zrobione

| Task | Status |
|------|--------|
| T1 Backend: `failed` retry, TG alert, queue `publish_failed`, `parse_publish_error` | Done |
| T3 UI: filtr Nieudane, liczniki, error box, Ponów publikację, link FB, fb-health strip | Done |
| T2 Ops: `check_token_health`, API `/marketing/fb-health`, skrypty deploy, runbook | Done |
| T4 Prewencja: `probe_media_url` przy create image (fail fast) | Done |

---

## Pliki kluczowe

| Plik | Zmiana |
|------|--------|
| `agent/publishers/facebook.py` | `parse_publish_error`, `check_token_health` |
| `agent/commander/publish.py` | retry z `failed`, notify, marketing agent touch |
| `agent/commander/publish_errors.py` | TG alert przy failed |
| `agent/commander/queue.py` | `publish_failed` CRITICAL |
| `api/routes/commander.py` | `GET /api/v1/commander/marketing/fb-health` |
| `commander-ui/*` | Marketing observability |
| `deployment/set-fb-access-token.py` | auto USER→PAGE exchange |
| `docs/ops/FB-TOKEN-ROTATION.md` | runbook rotacji tokenu |

---

## Testy lokalne

```bash
pytest tests/unit/test_publish_failure_notify.py \
       tests/unit/test_commander_queue.py \
       tests/unit/test_fb_token_health.py \
       tests/unit/test_content_calendar_media.py \
       tests/unit/test_commander_publish.py -q
```

---

## Deploy checklist (Zasada 11 — Dowódca / agent po approve)

```bash
# VPS
cd /opt/jadzia
cp data/jadzia.db data/jadzia.db.bak.$(date +%Y%m%d-%H%M%S)
git pull origin master
venv/bin/pip install -r requirements.txt
systemctl restart jadzia
systemctl is-active jadzia
```

**Smoke UI:**
1. Commander → Marketing → pasek „Facebook: Token OK (Page)”
2. Filtr **Nieudane** — widoczne wpisy z komunikatem błędu
3. **Ponów publikację** na failed (po OK tokenie)
4. Home → kolejka z `publish_failed` gdy są failed wpisy

---

## Walidacja prod (już potwierdzona przed Phase B)

- Wpis #16 „QR” opublikowany po rotacji Page Token
- `fb_post_id`: `491325420727745_122179733066613375`

---

## Backlog

| ID | Opis |
|----|------|
| M2 | Video/Reels publish |
| Long-lived FB token + expiry w settings | C3 z planu |
| COI-CMD-QUEUE-CLEAN | deploy02-* hot_leads |
