---
status: "[PRECLOSE · DEPLOY_READY]"
title: "VF-VHQ-DI-S6-MONEY — code ready, await GO DEPLOY"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S6-MONEY"
cache: "vhq-w64a"
scorecard_bump: "NO — only after prod dogfood"
---

# PRECLOSE — VF-VHQ-DI-S6-MONEY

## DONE

| Item | Result |
|------|--------|
| BLAST | written |
| `money_narrative.py` | lead counts + top_risk + Order PARKED · no euro KPI |
| `GET /money-risk` | wired |
| UI `#vhq-money-risk` | above NBA · cache `vhq-w64a` |
| pytest | money+nba+queue+escalation+api **30/30** |

## Deploy checklist

```text
1. backup jadzia-pre-di-s6-YYYYMMDD.db
2. chown commander-ui if needed → git pull → tip
3. restart jadzia
4. dogfood ?v=vhq-w64a&vhq=mc — Money/risk strip · EV-W2-010 · no euro green
5. CLOSE + S6=5 → next S3-APPROVAL
```
