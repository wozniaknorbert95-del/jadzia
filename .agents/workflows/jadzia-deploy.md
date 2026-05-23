---
description: VPS deploy runbook — Zasada 11, Commander executes.
---

# /jadzia-deploy

## Goal

Manual production deploy to VPS — agent outputs checklist; **Commander runs commands**.

## Preconditions

- [ ] `/jadzia-test` PASS
- [ ] `/audit-red-team` PASS
- [ ] Git pushed to `origin` (branch merged as per team policy)
- [ ] Commander available for SSH

## Reference docs

- [docs/PRD-core.md](../../docs/PRD-core.md) — deploy flow steps 1–7
- [flexgrafik-meta/docs/core/vps-ops.md](https://github.com/wozniaknorbert95-del/bouwplaats-chaos/blob/main/docs/core/vps-ops.md) — runbook
- Script: [deployment/deploy-to-vps.sh](../../deployment/deploy-to-vps.sh)

## Commander checklist (copy-paste block)

```text
1. Backup DB on VPS:
   sqlite3 /root/jadzia/data/jadzia.db ".backup /root/jadzia/backups/pre-deploy-$(date +%Y%m%d-%H%M%S).db"
2. From dev machine (review diff first):
   ./deployment/deploy-to-vps.sh
   OR manual: git pull, pip install -r requirements.txt, alembic upgrade head
3. Restart: sudo systemctl restart jadzia.service
4. Smoke: curl -f localhost:8000/health
5. Logs: journalctl -u jadzia -n 50
FAIL? → rollback per PRD-core.md
```

## Output

```text
DEPLOY_STATUS: AWAIT_COMMANDER
CHECKLIST: [preconditions verified yes/no]
COMMANDS: [numbered list above]

---
CURRENT_STAGE: F5-Launch
RECOMMENDED_NEXT: /handoff
WHY_NEXT: Record prod outcome after Commander confirms
---
```
