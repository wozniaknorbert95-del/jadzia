# VF-VHQ-W7-DOGFOOD — evidence NOTES

**Date:** 2026-07-31  
**URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a  
**VPS tip:** `f98c7b6` (docs stamp) · runtime feature `06212d7` · cache `vhq-w60a`  
**Auth:** JWT role `dowodca` (wiped after dogfood)  
**Worker:** healthy · `ssh_connection=ok`

## Timer (Command View Q1–Q7)

| Field | Value |
|-------|--------|
| Start | MC visible `?vhq=mission-control` (alias `mc`) |
| Elapsed | **994 ms** |
| Within ≤30s | **YES** |

## Q1–Q7 (ARCH §C)

| # | Question | Answer from UI |
|---|----------|----------------|
| Q1 | What is making money now? | Sales LIVE EV-W2-007 · Wizard LIVE EV-W2-005 · queue rail |
| Q2 | What is blocked or at risk? | Order Desk PARKED EV-W2-010 · flow break visible |
| Q3 | What needs my decision today? | Priorities/queue + Vault strip **pending 1** · EV-W6-001 |
| Q4 | Which department is behind? | Pulse/pins: Agent Ops PARTIAL · Finance UNVERIFIED · Marketing UNVERIFIED |
| Q5 | Which agent/action failed or waits? | Vault L3 pending · worker ssh ok · Agent Ops PARTIAL EV-W2-011 |
| Q6 | What is the next best action? | Director actions: Focus priorities/queue · Open Vault · Open Wizard |
| Q7 | What is not trusted / not implemented? | Order PARKED EV-W2-010 · Marketing UNVERIFIED EV-W3-001 · Vault PARTIAL · Finance UNVERIFIED EV-W2-008 |

## MVP rooms

| Room | Status | Evidence |
|------|--------|----------|
| mission-control | LIVE | EV-W2-001 · w7-01-mc.png |
| wizard-quote | LIVE | EV-W2-005 · bus trail · w7-02-wizard.png |
| sales-room | LIVE | EV-W2-007 · w7-05-sales.png |
| approval-vault | PARTIAL | EV-W6-001 · L3 STOP · 0 Approve · w7-03-vault.png |
| ai-agent-health | PARTIAL | EV-W2-011 |
| marketing-studio | UNVERIFIED | EV-W3-001 |
| order-desk | PARKED | EV-W2-010 · w7-04-order.png |
| analytics-finance | UNVERIFIED | EV-W2-008 |

## STOP held

No Order LIVE · no Ads/Mollie · no 3D · no MKT · no runtime change
