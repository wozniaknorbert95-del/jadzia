---
status: "[CLOSED]"
title: "DEPLOY-VHQ-W6-00 — Approval Vault LIVE"
updated: "2026-07-31"
gate: "DEPLOY-VHQ-W6-00"
prod_tip: "06212d7"
runtime_commit: "06212d7"
docs_tip: "06212d7"
cache_asset: "vhq-w60a"
rollback: "43a88d2"
rollback_cache: "vhq-w50a"
backup: "/opt/jadzia/data/jadzia-pre-vhq-w6-20260731-090936.db"
---

# Handoff — 2026-07-31 — DEPLOY-VHQ-W6-00

## Verdict

**DEPLOY PASS** + **PRODUCTION VERIFY PASS** (Vault UX + L2/L3 honesty)

## Sequence

| Step | Result |
|------|--------|
| W6 CLOSE local | DONE · dogfood PASS · pytest 10/10 |
| COMMIT W6 allowlist | **`06212d7`** |
| Push `origin/master` | `43a88d2..06212d7` |
| VPS pre tip | **`43a88d2`** |
| VPS backup | `/opt/jadzia/data/jadzia-pre-vhq-w6-20260731-090936.db` |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`06212d7`** |
| Cache `vhq-w60a` + vault panel | **OK** |
| `systemctl restart jadzia` | **active** |
| `/health` + `/worker/health` | OK · `ssh_connection=ok` |
| Prod asset | `styles.css?v=vhq-w60a` · `app.js?v=vhq-w60a` |
| Prod API L2 approve | **ok** · `side_effects=false` |
| Prod API L3 approve | **403** · Founder GO |
| Prod UI Vault | L3 STOP · **0 Approve buttons** |
| Prod UI Order Desk | PARKED · EV-W2-010 |
| MKT / Ads / Mollie | **none** |

## Cache token

| Role | Token |
|------|-------|
| Asset bust + public URL | **`vhq-w60a`** |
| Service Worker | `coi-commander-shell-vhq-w60a` |

```text
Primary: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a
Vault:   https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a&vhq=approval-vault
Order:   https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a&vhq=order-desk
```

## Rollback

| Item | Value |
|------|-------|
| Rollback SHA | `43a88d2` |
| Rollback cache | `vhq-w50a` |
| Hard rollback | `cd /opt/jadzia && git checkout 43a88d2 && systemctl restart jadzia` then `?v=vhq-w50a` |

## Explicit non-actions

- No MKT commit  
- No Ads / Mollie / Gate D  
- No Order Desk LIVE  
- No silent L3/L4  

## Evidence

- Local: `docs/handoffs/evidence-vhq-w60-dogfood/`
- Prod: `docs/handoffs/evidence-vhq-w60-prod-dogfood/`
- Feature CLOSE: `docs/handoffs/2026-07-31-VF-VHQ-W6-DIRECTOR-APPROVALS-CLOSE.md`
