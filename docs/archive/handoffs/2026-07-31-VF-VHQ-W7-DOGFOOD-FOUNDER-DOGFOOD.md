---
status: "[STAMPED-PASS]"
title: "VF-VHQ-W7 — Founder dogfood PASS (≤30s + honest gaps)"
updated: "2026-07-31"
gate: "VF-VHQ-W7-DOGFOOD"
cache: "vhq-w60a"
prod_url: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a"
runtime_commit: "06212d7"
vps_tip: "f98c7b6"
jwt: true
elapsed_ms: 994
evidence_dir: "docs/handoffs/evidence-vhq-w7-dogfood/"
---

# VF-VHQ-W7 — Founder dogfood PASS

**Prod URL:** `https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a`  
**Auth:** JWT · **Timer:** 994 ms (≤30s)  

## Checklist

| # | Step | Expected | Result |
|---|------|----------|--------|
| 1 | Preflight tip/cache/JWT/worker | `vhq-w60a` · JWT · ssh ok | **PASS** |
| 2 | Q1–Q7 Command View ≤30s | All answered or honest gap | **PASS** · 994 ms |
| 3 | MC vault strip | pending count real | **PASS** · pending 1 |
| 4 | Wizard / Sales LIVE | EV-W2-005 / EV-W2-007 | **PASS** |
| 5 | Approval Vault PARTIAL | Ops Bus · L3 STOP · no Approve | **PASS** |
| 6 | Order Desk | PARKED · EV-W2-010 | **PASS** |
| 7 | Marketing / Finance pins | UNVERIFIED | **PASS** |
| 8 | AI Agent Health | PARTIAL EV-W2-011 | **PASS** |
| 9 | No Order LIVE / Ads / Mollie / 3D / MKT | STOP held | **PASS** |
| 10 | Evidence pack | NOTES + screenshots | **PASS** |

## Stamp

```text
FOUNDER STAMP: PASS
Date: 2026-07-31
Notes: Implement plan = GO. Q1–Q7 ≤30s on prod vhq-w60a + JWT. Honest gaps accepted. 3D remains parked.
```
