---
status: "[AGENT-DOGFOOD-PASS]"
title: "VF-VHQ-W4 LIVE — agent prod dogfood"
updated: "2026-07-31"
cache: "vhq-w40b"
prod_url: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w40b"
prod_tip: "78fa49d"
runtime_ui_tip: "b6d0d36"
---

# VF-VHQ-W4 LIVE — Agent prod dogfood

**Date:** 2026-07-31  
**URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w40b  
**Method:** Chrome DevTools `evaluate_script`  
**Verdict:** **PASS**

| # | Check | Result |
|---|-------|--------|
| 1 | Cache `vhq-w40b` · `data-vhq-w4=1` | **PASS** |
| 2 | Cold-open Mission Control | **PASS** |
| 3 | Order Desk PARKED EV-W2-010 · insufficient_data · no LIVE | **PASS** |
| 4 | Production PARKED EV-W4-001 | **PASS** |
| 5 | Preflight PLANNED EV-W4-002 | **PASS** |
| 6 | Dispatch PARKED EV-W4-003 | **PASS** |
| 7 | Wizard handoff EV-W2-010 → Order WV | **PASS** |
| 8 | Truth Card Order EV-W2-010 | **PASS** |
| 9 | Flow break EV-W2-010 | **PASS** |
| 10 | Marketing UNVERIFIED EV-W3-001 | **PASS** |
| 11 | Legacy `?vhq_shell=legacy` loads | **PASS** (navigated) |
| 12 | No Ads/Mollie from ops surfaces | **PASS** |

Founder stamp pack: `docs/handoffs/2026-07-31-VF-VHQ-W4-ROOMS-OPERATIONS-FOUNDER-DOGFOOD.md` (`founder_stamp: pending`)
