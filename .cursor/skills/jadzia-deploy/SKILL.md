---
name: jadzia-deploy
description: >-
  VPS deploy checklist for jadzia-core — Commander executes; agent prepares only (Zasada 11).
disable-model-invocation: true
---

# /jadzia-deploy

## Goal

Prepare manual VPS deploy — **AWAIT_COMMANDER** for all SSH/systemctl actions.

## Canonical workflow

- **[.agents/workflows/jadzia-deploy.md](../../.agents/workflows/jadzia-deploy.md)**

## Don't

- Run `deployment/deploy-to-vps.sh` autonomously
- Restart `jadzia.service` without Commander approval
- Deploy without `/jadzia-test` PASS + `/audit-red-team` PASS

## Output

```text
DEPLOY_STATUS: AWAIT_COMMANDER
CHECKLIST: [see workflow]
COMMANDS: [for Commander copy-paste only]

---
CURRENT_STAGE: F5-Launch
RECOMMENDED_NEXT: /handoff
WHY_NEXT: Confirm prod state after Commander deploy
---
```
