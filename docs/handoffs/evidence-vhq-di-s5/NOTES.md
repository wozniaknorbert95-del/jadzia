# Evidence — VF-VHQ-DI-S5-NBA prod dogfood

**When:** 2026-07-31  
**Tip:** `81372dd` (feature `a044612`) · cache `vhq-w63a`  
**URL:** `https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w63a&vhq=mc`

## Checks

| Check | Result |
|-------|--------|
| Pre-deploy pytest | 27/27 |
| Local smoke NBA | PASS |
| VPS tip | `81372dd` after chown + `git reset --hard origin/master` |
| VPS brief | NBA=`sales_cta` lead #10 score 89.018 L1; SEC=`fb_post_pending`; not stale/stub |
| UI NBA card | **1** — Director: do this now · Why now · Owner · Evidence · Cost · Score · CTA Potwierdź lead |
| Secondary | Case study 3149 only |
| Analytics stale in Decide-now | ABSENT |
| Order PARKED | EV-W2-010 |
| Ops | OK · data confidence degraded (not fire) |
| ≤30s Q3+Q6 | PASS — primary CTA + why-now visible above fold |

## Ops note

First `git pull` failed unlinking `commander-ui/*` (perms). Fixed via `chown -R jadzia:jadzia` + hard reset. Prefer keep `commander-ui` owned by `jadzia`.
