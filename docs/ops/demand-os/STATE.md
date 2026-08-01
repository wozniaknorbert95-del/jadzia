---
status: "[ACTIVE · GO TIKTOK ORGANIC LIVE]"
title: "Demand OS — execution state machine"
updated: "2026-08-01"
gate: "DEMAND-OS-F0-ORGANIC-00"
last_step: "GO TIKTOK ORGANIC TODAY"
last_result: "ARMED"
---

# Demand OS — STATE

| Pole | Wartość |
|------|---------|
| phase | `F0_ORGANIC_LIVE` |
| organic_from | `2026-08-01` (**GO TODAY**) |
| command | `GO TIKTOK ORGANIC` **ACTIVE** |
| ads_freeze_until | `2026-08-06` |
| build_unlocked | **false** |
| deploy_vps | **STOP** |
| next_human | Publish **tt_w31_install_01** NOW → reply `PUBLISHED tt_w31_install_01` |
| next_agent | On `PUBLISHED…`: set LEDGER publish=Y · Validator publish_intended=Y · advance W1-03 |

## next_action

```text
HUMAN NOW: open GO-DAY-TODAY.md → publish tt_w31_install_01
AGENT: wait for PUBLISHED signal OR keep supporting captions #2/#3
THEN: ledger daily · ≥3 TT this week · Money Check 2026-08-03
NO: deploy · dashboard · Ads · code until W1-PASS
```
