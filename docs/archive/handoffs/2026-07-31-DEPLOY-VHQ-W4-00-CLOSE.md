---
status: "[CLOSED]"
title: "DEPLOY-VHQ-W4-00 — Ops Work Views LIVE"
updated: "2026-07-31"
gate: "DEPLOY-VHQ-W4-00"
prod_tip: "b6d0d36"
runtime_commit: "b6d0d36"
cache_asset: "vhq-w40b"
rollback: "de10e83"
rollback_cache: "vhq-w32a"
---

# Handoff — 2026-07-31 — DEPLOY-VHQ-W4-00

## Verdict

**DEPLOY PASS** + **PRODUCTION DOGFOOD PASS**

## Sequence

| Step | Result |
|------|--------|
| W4 CLOSE | DONE (Founder GO verify+commit+deploy) |
| Professional P1 polish | flow/Wizard EV-W2-010 · SW `vhq-w40b` · focus · explicit DOM map |
| COMMIT W4 ONLY | **`b6d0d36`** `feat(vhq): honest ops Work Views… (W4)` |
| Push `origin/master` | `de10e83..b6d0d36` |
| VPS pre tip | **`de10e83`** |
| VPS backup | `/opt/jadzia/data/jadzia-pre-vhq-w4-20260731-074202.db` |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`b6d0d36`** |
| `systemctl restart jadzia` | **active** |
| `/health` | OK (`Strona OK`) |
| `/worker/health` | **degraded** SSH (pre-existing; did not block UI deploy) |
| Prod asset smoke | `styles.css?v=vhq-w40b` + `data-vhq-w4=1` |
| Prod dogfood `?v=vhq-w40b` | **PASS** (4 ops WV + Wizard EV + Truth + flow) |
| MKT / Ads / Mollie | **none** |

## Cache token

| Role | Token |
|------|-------|
| Asset bust + public URL query | **`vhq-w40b`** |
| Service Worker | `coi-commander-shell-vhq-w40b` |

```text
Primary: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w40b
Console: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w40b&vhq=console
Legacy:  https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w40b&vhq_shell=legacy
```

## Rollback

| Item | Value |
|------|-------|
| Rollback SHA | `de10e83` |
| Rollback cache | `vhq-w32a` |
| Hard rollback | `cd /opt/jadzia && git checkout de10e83 && systemctl restart jadzia` then `?v=vhq-w32a` |

## Production dogfood

| Check | Result |
|-------|--------|
| Cache hint `vhq-w40b` · `data-vhq-w4=1` | **PASS** |
| Cold-open MC | **PASS** |
| Order Work View PARKED EV-W2-010 · insufficient_data · no LIVE | **PASS** |
| Production PARKED EV-W4-001 | **PASS** |
| Preflight PLANNED EV-W4-002 | **PASS** |
| Dispatch PARKED EV-W4-003 | **PASS** |
| Wizard handoff button + open Order WV with EV-W2-010 | **PASS** |
| Truth Card Order EV-W2-010 | **PASS** |
| Flow break EV-W2-010 | **PASS** |
| `/health` OK · worker SSH degraded (known) | **PASS** (UI) |

## Explicit non-actions

- No MKT commit  
- No Ads / Mollie / Gate D  
- No W5 activation  
- No fake Order Desk LIVE  
