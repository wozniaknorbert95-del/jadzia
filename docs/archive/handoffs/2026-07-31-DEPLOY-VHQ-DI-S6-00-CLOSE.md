---
status: "[DEPLOY CLOSE]"
title: "DEPLOY VF-VHQ-DI-S6-MONEY"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S6-MONEY"
founder_go: "GO DEPLOY (session 2026-07-31)"
prod_tip: "0d1407f"
feature_tip: "f77989c"
backup: "/opt/jadzia/data/jadzia-pre-di-s6-20260731.db"
---

# DEPLOY CLOSE — DI-S6

1. Backup OK  
2. `chown` + `git reset --hard origin/master` → **0d1407f**  
3. Restart · health OK  
4. VPS smoke + JWT dogfood `?v=vhq-w64a` PASS  

## Rollback

```text
cd /opt/jadzia && git checkout 3a9951c && systemctl restart jadzia
```
