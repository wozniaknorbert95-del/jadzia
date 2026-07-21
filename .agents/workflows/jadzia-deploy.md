---
description: L4 - Production release (agent executes under GO; else Commander pack).
---

# /jadzia-deploy

## Goal

Safe deploy to VPS `/opt/jadzia`. Prefer invoking from `/post-coding` during closeout.

## Authority (Zasada 11)

| Condition | Who runs SSH |
|-----------|----------------|
| `todo.standing_go_closeout === true` | **Agent** |
| Explicit GO in current session | **Agent** |
| Neither | Agent prepares COMMAND_BLOCK; **Commander** executes |

Hard STOP without separate GO: Gate D, Mollie LIVE, secrets, merge OS↔jadzia.

## Pre-conditions

- [ ] Tests relevant to change PASS (or docs-only tip sync)
- [ ] Pushed to `origin/master`
- [ ] SQLite backup when runtime/schema touches DB

## Agent execution (when authorized)

Canonical runtime deploy:

```bash
bash /tmp/rev-demand-01-deploy-vps.sh <expected_sha>
# or after scp: deployment/rev-demand-01-deploy-vps.sh
```

Docs-only tip sync (no restart):

```bash
cd /opt/jadzia && git pull --ff-only origin master && git rev-parse --short HEAD
```

Post-checks:

```bash
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health
```

## Commander pack (no GO)

```bash
# 1. Backup
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-deploy-$(date +%Y%m%d-%H%M%S).db'"

# 2. Pull
cd /opt/jadzia && git fetch origin master && git pull --ff-only origin master

# 3. Deps + restart (runtime only)
sudo -u jadzia bash -lc 'cd /opt/jadzia && source venv/bin/activate && if [ -f requirements.lock ]; then pip install --require-hashes -r requirements.lock -q; else pip install -r requirements.txt -q; fi'
systemctl restart jadzia
sleep 4
curl -sf http://127.0.0.1:8000/health
```

## Output

```text
DEPLOY_STATUS: DONE | AWAIT_COMMANDER | ABORT
TIP: …
HEALTH: OK | FAIL
ROLLBACK: git checkout <prev> && systemctl restart jadzia

---
CURRENT_STAGE: L4-Release
RECOMMENDED_NEXT: /handoff | /post-coding evidence step
---
```
