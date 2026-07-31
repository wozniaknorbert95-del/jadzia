---
status: "[CLOSED]"
title: "VF-VHQ-FIRM-IA-00 — local CLOSE PASS, deploy pending"
updated: "2026-07-31"
verdict: "CLOSED LOCAL PASS"
tip: "a05e762"
runtime_tip: "2623ae2"
cache: "vhq-w66a"
active_gate: "VF-VHQ-FIRM-IA-00"
deploy_status: "pending_go_deploy"
---

# CLOSE — VF-VHQ-FIRM-IA-00

## Decision

FIRM-IA local closeout is **PASS** on contracts + static source verification.  
Deploy is **not executed**. Founder prod dogfood on `?v=vhq-w66a` remains pending explicit `GO DEPLOY VF-VHQ-FIRM-IA-00`.

## Verification

### Pytest slice

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py tests/unit/test_commander_money_narrative.py tests/unit/test_commander_nba.py -v
```

Result: **17 passed / 0 failed**.

### Local dogfood checklist

Browser walk was not executed in this task window. Below is **CONTRACT + STATIC** evidence from source, with prod Founder click-dogfood explicitly pending deploy GO.

| Item | Method | Result | Evidence |
|------|--------|--------|----------|
| Cold open HQ / Mission Control | Static | PASS | `commander-ui/index.html` starts on `view-hq` active; `commander-ui/app.js` `vhqGoMissionControl()` renders `mission-control` in primary shell |
| Esc room → MC; second Esc stays HQ | Pytest + static | PASS | `tests/unit/test_vhq_firm_ia_contracts.py`; `commander-ui/app.js` `vhqEscLadder()` returns to `mission-control` and stops there |
| Tools / Sign in → Console → Return to HQ | Static | PASS | `commander-ui/index.html` exposes `#vhq-to-console` label `Tools / Sign in`; `commander-ui/app.js` binds `vhqGoConsole()` and `#vhq-enter` back to HQ |
| Firm Chain visible; stages dim correctly | Pytest + static | PASS | `commander-ui/index.html` contains `#vhq-firm-chain`; `commander-ui/app.js` `vhqSetFirmStageFilter()` toggles active/dim state |
| Order Desk PARKED + role + unlock; no euro KPI | Pytest + static | PASS | `commander-ui/app.js` `VHQ_ROOMS["order-desk"]` keeps `EV-W2-010`, `firmRole`, `unlockHint`; order view says no operational desk / no invented board |
| NBA + money-risk + Vault still on MC | Pytest + static | PASS | `commander-ui/index.html` keeps `#vhq-money-risk`, `#vhq-nba`, `#vhq-open-vault` inside Mission Control block |

## Scope closed

- FIRM-IA shell primacy preserved: Console demoted to explicit tools path only
- Firm Chain IA preserved: `demand → sell → deliver → direct`
- Order Desk remains honest `PARKED`; no fake S7 reopen, no invented ops KPI
- Cache target for next prod dogfood is `vhq-w66a`

## STOP unchanged

No deploy without GO · no fake Order Desk LIVE · no Mollie/Purchase unlock · no Ads/premium spend unlock · no MKT dirty files in commit.

## Next

```text
active_gate = VF-VHQ-FIRM-IA-00
next_agent = wait for GO DEPLOY → prod Founder dogfood on vhq-w66a → deploy CLOSE
```
