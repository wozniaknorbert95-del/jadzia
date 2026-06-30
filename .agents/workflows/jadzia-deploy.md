---
description: L4 - Production Release Runbook.
---

# /jadzia-deploy

## 🎯 Goal
Safe, manual deployment to the bare-metal VPS. Following **Zasada 11**: Agent prepares, Commander executes.

## 🛑 Pre-conditions (The "No-Go" List)
The deploy is ABORTED if any of these are NO:
- [ ] `/jadzia-test` $\to$ PASS
- [ ] `/audit-red-team` $\to$ PASS
- [ ] Git pushed to `origin`
- [ ] DB Backup strategy confirmed

## 🛠️ Deployment Procedure

### 1. Preparation
Agent provides the Commander with the exact sequence of commands.

### 2. Execution Block (Copy-Paste for Commander)
```bash
# 1. Backup current DB
sqlite3 /opt/jadzia/data/jadzia.db ".backup /opt/jadzia/backups/pre-deploy-$(date +%Y%m%d-%H%M%S).db"

# 2. Pull latest code
cd /opt/jadzia && git pull origin main

# 3. Update dependencies
source venv/bin/activate && pip install -r requirements.txt

# 4. Database Migrations (if applicable)
alembic upgrade head

# 5. Restart Service
sudo systemctl restart jadzia.service

# 6. Health Check
curl -f localhost:8000/health
```

### 3. Post-Deploy Validation
- **Logs**: `journalctl -u jadzia -n 100` $\to$ Check for startup errors.
- **Worker**: Verify that `api/app.py` worker loop is picking up tasks.

## 📤 Output Format

```text
DEPLOY_STATUS: AWAIT_COMMANDER
PRECONDITIONS: [ALL PASS | FAIL: X]
COMMAND_BLOCK: [The bash block above]
ROLLBACK_PLAN: [e.g., 'git checkout <prev_hash> && systemctl restart']

---
CURRENT_STAGE: L4-Release
RECOMMENDED_NEXT: /handoff
WHY_NEXT: Deploy finished; need to synchronize state.
---
```
