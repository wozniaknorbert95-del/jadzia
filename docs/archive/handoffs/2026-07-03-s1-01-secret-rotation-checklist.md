# Checklist: S1-01 Secret Rotation (Dowódca — human only)

**Status:** BLOCKED on human — agent cannot execute  
**Priority:** CRITICAL (P0 from audit)

## Secrets to rotate

1. `ANTHROPIC_API_KEY`
2. `JWT_SECRET` (update all clients: Telegram bot, scripts, Mission Control)
3. `SSH_PASSWORD` or confirm key-only SSH
4. `TELEGRAM_BOT_TOKEN`
5. `WC_WEBHOOK_SECRET` — sync zzpackage `FG_JADZIA_WEBHOOK_SECRET` in wp-config
6. `LEADS_API_KEY` — sync app.flexgrafik.nl sender
7. `FB_ACCESS_TOKEN` (INT-011)
8. Google Cloud key (historical exposure from deleted `list_models.py`)

## Cross-module sync

| Secret | jadzia VPS | zzpackage | app |
|--------|------------|-----------|-----|
| WC webhook | `WC_WEBHOOK_SECRET` | `FG_JADZIA_WEBHOOK_SECRET` | — |
| Leads | `LEADS_API_KEY` | — | X-API-Key header |

## Git history cleanup

```bash
# After all keys rotated and verified live:
pip install git-filter-repo
git filter-repo --invert-paths --path list_models.py  # if still in history
# Force push ONLY after Dowódca approval — coordinate with team
```

## Verification after rotation

1. `bash deployment/prod-smoke.sh` — all OK
2. INT-002 synthetic order (wp-cli or test checkout)
3. INT-004 lead POST from app
4. Worker task via JWT (`scripts/send_task.py`)

## Handoff when done

Create `docs/handoffs/YYYY-MM-DD-s1-01-secret-rotation-proof.md` and mark `S1-01` completed in `todo.json`.
