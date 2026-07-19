# Handoff — 2026-07-09 COI Marketing (M1 + Phase B deploy)

**Branch:** `master` @ `0f9ce1e`  
**VPS:** `185.243.54.115` `/opt/jadzia` @ `1036d6e` — `jadzia` **active**  
**Public:** https://api.zzpackage.flexgrafik.nl/commander/

---

## DONE

| Gate / program | Wynik |
|----------------|-------|
| COI Commander v3 | merged, prod, workshop |
| COI-CONTENT-INTAKE-M1 | composer, GDrive URL, FB photo publish |
| COI-MARKETING-PUBLISH-B | failed UX, TG alert, `publish_failed` queue, fb-health, retry, GDrive probe |
| FB ops | Page token prod, `exchange-fb-page-token`, runbook `FB-TOKEN-ROTATION.md` |
| E2E prod | wpis #16 „QR” → `published`, `fb_post_id` `491325420727745_122179733066613375` |

**Commits sesji (master):** `d40d0d8` M1 → `1036d6e` Phase B → `0f9ce1e` session close

**Testy (lokalnie):** Phase B suite 17+ pass (`test_publish_failure_notify`, `test_fb_token_health`, `test_commander_queue`, `test_content_calendar_media`)

**Prod smoke:** `/commander/` 200, FB token type PAGE valid, calendar entry #16 published

---

## LEFT

| ID | Task | Owner | Priorytet |
|----|------|-------|-----------|
| COI-CMD-QUEUE-CLEAN | Usuń E2E `deploy02-*` hot_leads z Home | agent | **next** |
| COI-CONTENT-INTAKE-M2 | Video/Reels publish | agent | po OK flow |
| COI-CMD-SMTP-01 | SMTP + email eskalacji Delegata | Dowódca + agent | medium |
| FB token rotacja | Nowy token, unieważnij stary (był w czacie) | Dowódca | higiena |
| Long-lived Page token | Server-side exchange + expiry w settings | backlog | ops |
| INSPIRE engine | unstaged lokalnie — osobny commit/track | agent | osobno |

**Human (2 min):** Commander → Marketing → fb-health strip + filtr Nieudane/Opublikowane + wpis QR

---

## RISKS

- FB token w czacie — rotacja zalecana (`docs/ops/FB-TOKEN-ROTATION.md`)
- Token Explorer krótkotrwały — wygasa ~lipiec 2026 (`expires_at`); brak long-lived automation
- SMTP brak w `.env` — email eskalacji nie wychodzi (TG działa)
- `probe_media_url` przy create — może false-negative na bardzo dużych plikach GDrive

---

## Refs

- `docs/handoffs/2026-07-09-coi-content-intake-m1-PROOF.md`
- `docs/handoffs/2026-07-09-coi-marketing-publish-B-PROOF.md`
- `docs/ops/FB-TOKEN-ROTATION.md`
- `docs/ops/COI-MARKETING-GDRIVE-SETUP.md`

---

## Deploy checklist (już wykonane 2026-07-09)

```bash
cd /opt/jadzia
cp data/jadzia.db data/jadzia.db.bak.$(date +%Y%m%d-%H%M%S)
git pull origin master
venv/bin/pip install -r requirements.txt
systemctl restart jadzia
```

---

## Następna sesja agenta

1. `@blast` → `COI-CMD-QUEUE-CLEAN` (15 min, czyści Home)
2. Po Dowódcy OK na marketing flow → `@blast` → `COI-CONTENT-INTAKE-M2`
