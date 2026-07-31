---
status: "[PRECLOSE · DEPLOY_READY]"
title: "VF-VHQ-DI-S4-SNR-FINISH — code shipped, await GO DEPLOY"
updated: "2026-07-31"
gate: "VF-VHQ-DI-S4-SNR-FINISH"
scorecard_bump: "NO — only after prod dogfood"
cache: "vhq-w62a (API-only, no bump)"
---

# PRECLOSE — VF-VHQ-DI-S4-SNR-FINISH

## DONE (local / origin after ship)

| Item | Result |
|------|--------|
| BLAST | `docs/handoffs/2026-07-31-VF-VHQ-DI-S4-SNR-FINISH-BLAST.md` |
| Code | `QUEUE_SEVERITY["analytics_stale"]` = **INFO** |
| Test | `test_analytics_stale_is_info_not_decide_now` |
| pytest | `test_commander_queue` + `test_commander_escalation` **10/10** |
| UI | none |
| MKT staged | NO |

## DoD progress

| # | Status |
|---|--------|
| S4.1 stubs 0% | regression — verify on dogfood |
| S4.2 freshness not Ops fire | regression — verify on dogfood |
| S4.3 analytics_stale not Decide-now ACTION | **unit PASS** · prod pending |
| S4.4 noise &lt;10% | prod dogfood pending |
| S4.5 evidence | pending |

## STOP until GO DEPLOY

- No scorecard S4→5
- No pop `closeout_queue`
- No invent dogfood

## Deploy checklist (Commander / agent with GO)

```text
1. ssh vcms-vps
2. sudo -u jadzia cp /opt/jadzia/data/jadzia.db /opt/jadzia/data/jadzia-pre-di-s4-$(date +%Y%m%d).db
3. cd /opt/jadzia && sudo -u jadzia git pull --ff-only origin master
4. sudo systemctl restart jadzia
5. curl -sS https://api.zzpackage.flexgrafik.nl/health
6. systemctl is-active jadzia; journalctl -u jadzia -n 30 --no-pager
7. Dogfood JWT: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w62a&vhq=mc
   - Decide-now: NO "Analytics stale: GA4"
   - stubs 0% · Ops confidence line OK · Order PARKED EV-W2-010
8. Evidence → docs/handoffs/evidence-vhq-di-s4/ · CLOSE + scorecard S4=5 · next S5
```

## Next after GO + dogfood PASS

`/vhq-decision-instrument` CLOSE S4 → active `VF-VHQ-DI-S5-NBA`
