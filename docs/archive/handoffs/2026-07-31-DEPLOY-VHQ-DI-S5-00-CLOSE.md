---
status: "[DEPLOY CLOSE]"
title: "DEPLOY VF-VHQ-DI-S5-NBA"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S5-NBA"
founder_go: "verify then deploy (session 2026-07-31)"
prod_tip: "81372dd"
feature_tip: "a044612"
backup: "/opt/jadzia/data/jadzia-pre-di-s5-20260731.db"
---

# DEPLOY CLOSE — DI-S5

1. VERIFY local 27/27 + smoke — PASS (`evidence-vhq-di-s5/VERIFY-DEPLOY-READY.md`)
2. Backup DB — OK
3. Pull blocked on `commander-ui` perms → `chown` + `git reset --hard origin/master` → **81372dd**
4. Restart jadzia — active · health OK
5. VPS NBA smoke + JWT dogfood `?v=vhq-w63a` — PASS

## Rollback

```text
cd /opt/jadzia && git checkout 4ac31d9 && systemctl restart jadzia
```
