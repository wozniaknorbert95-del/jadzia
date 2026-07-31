---
status: "[CLOSED]"
title: "DEPLOY-VHQ-W5-00 — Operations Bus LIVE"
updated: "2026-07-31"
gate: "DEPLOY-VHQ-W5-00"
prod_tip: "476d1bf"
runtime_commit: "174603e"
docs_tip: "476d1bf"
runtime_deploy_tip: "67700ff"
cache_asset: "vhq-w50a"
rollback: "6375ab1"
rollback_cache: "vhq-w40c"
backup: "/opt/jadzia/data/jadzia-pre-vhq-w5-20260731-082855.db"
---

# Handoff — 2026-07-31 — DEPLOY-VHQ-W5-00

## Verdict

**DEPLOY PASS** + **PRODUCTION VERIFY PASS** (API bus + honesty UI)

## Sequence

| Step | Result |
|------|--------|
| W5 CLOSE local | DONE · dogfood PASS |
| COMMIT W5 allowlist | **`174603e`** + tip **`67700ff`** |
| pytest ops_bus + Commander smoke | **10/10 PASS** |
| Push `origin/master` | `6375ab1..67700ff` |
| VPS pre tip | **`6375ab1`** |
| VPS backup | `/opt/jadzia/data/jadzia-pre-vhq-w5-20260731-082855.db` |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`67700ff`** |
| Schema `ops_bus_events` | **present** after restart |
| `systemctl restart jadzia` | **active** |
| `/health` | OK |
| `/worker/health` | **healthy** · `ssh_connection=ok` |
| Prod asset | `styles.css?v=vhq-w50a` · `app.js?v=vhq-w50a` |
| Prod API ingest `wizard_started` | **ok** · EV-W5-002 |
| Prod UI Order Desk | PARKED · EV-W2-010 · no LIVE |
| MKT / Ads / Mollie | **none** |

## Cache token

| Role | Token |
|------|-------|
| Asset bust + public URL | **`vhq-w50a`** |
| Service Worker | `coi-commander-shell-vhq-w50a` |

```text
Primary: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w50a
Wizard:  https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w50a&vhq=wizard-quote
Order:   https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w50a&vhq=order-desk
```

## Rollback

| Item | Value |
|------|-------|
| Rollback SHA | `6375ab1` |
| Rollback cache | `vhq-w40c` |
| Hard rollback | `cd /opt/jadzia && git checkout 6375ab1 && systemctl restart jadzia` then `?v=vhq-w40c` |
| Soft kill-switch | `ops_bus_enabled=false` in commander_settings |

## Explicit non-actions

- No MKT commit  
- No Ads / Mollie / Gate D  
- No Order Desk LIVE  
- No silent L3/L4  
- No full catalog beyond cash spine (residual → SoT report)

## Evidence

- Local: `docs/handoffs/evidence-vhq-w50-dogfood/`
- Prod: `docs/handoffs/evidence-vhq-w50-prod-dogfood/`
- Dogfood notes: `docs/handoffs/2026-07-31-VF-VHQ-W5-OPERATIONS-BUS-FOUNDER-DOGFOOD.md`
- SoT gap report: `docs/handoffs/2026-07-31-VF-VHQ-W5-SOT-CONSISTENCY-REPORT.md`
