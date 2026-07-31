---
status: "[DEPLOY CLOSE]"
title: "DEPLOY VF-VHQ-DI-S4-SNR-FINISH"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S4-SNR-FINISH"
founder_go: "GO DEPLOY (session 2026-07-31)"
prod_tip: "c56b13e"
feature_tip: "35259b4"
backup: "/opt/jadzia/data/jadzia-pre-di-s4-20260731.db"
---

# DEPLOY CLOSE — DI-S4

## Steps

1. Backup `jadzia-pre-di-s4-20260731.db` — OK  
2. First pull failed: `.git/objects` perms → `chown -R jadzia:jadzia .git` — fixed  
3. `git pull --ff-only` **6e357cc → c56b13e** — OK  
4. `systemctl restart jadzia` — active  
5. `/health` — `status=ok`  
6. constants on disk: `analytics_stale": "INFO"`  
7. Prod JWT dogfood PASS — see `evidence-vhq-di-s4/NOTES.md`

## Rollback

```text
cd /opt/jadzia && git checkout 6e357cc && systemctl restart jadzia
# or restore jadzia-pre-di-s4-20260731.db if data issue (unlikely for severity-only)
```
