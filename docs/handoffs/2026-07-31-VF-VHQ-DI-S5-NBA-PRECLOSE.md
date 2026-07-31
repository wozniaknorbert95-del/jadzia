---
status: "[PRECLOSE · DEPLOY_READY]"
title: "VF-VHQ-DI-S5-NBA — code ready, await GO DEPLOY"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S5-NBA"
cache: "vhq-w63a"
scorecard_bump: "NO — only after prod dogfood ≤30s"
---

# PRECLOSE — VF-VHQ-DI-S5-NBA

## DONE (local)

| Item | Result |
|------|--------|
| BLAST | `docs/handoffs/2026-07-31-VF-VHQ-DI-S5-NBA-BLAST.md` |
| `agent/commander/nba.py` | deterministic score + enrich |
| API `priorities/today` | `{nba, priorities, secondary, total}` |
| UI | `#vhq-nba` Director card · secondary below · cache `vhq-w63a` |
| pytest | nba+queue+escalation+api **27/27** |

## DoD

| # | Status |
|---|--------|
| S5.1–S5.3 · S5.5 | unit/UI ready |
| S5.4 dogfood ≤30s | pending GO DEPLOY |

## Deploy checklist

```text
1. backup jadzia.db → jadzia-pre-di-s5-YYYYMMDD.db
2. git pull --ff-only → tip with S5
3. systemctl restart jadzia
4. dogfood ?v=vhq-w63a&vhq=mc — exactly 1 NBA card · Q3+Q6 ≤30s
5. CLOSE + scorecard S5=5 → next S6-MONEY
```

## STOP until GO

No scorecard bump · no MKT · preserve EV-W2-010
