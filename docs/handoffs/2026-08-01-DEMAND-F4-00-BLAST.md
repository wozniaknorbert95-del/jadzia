---
status: "[BLAST · CLOSED LOCAL]"
title: "DEMAND-F4-00 — Blog ICP pipeline"
updated: "2026-08-01"
gate: "DEMAND-OS-F4-00"
todo: DOS-F4-01
founder_go: "GO BUILD demand-f4 (Dowódca: lecimy dalej z planu / build 2026-08-01)"
runtime_changes_allowed: false
deploy_vps: false
---

# BLAST — DEMAND-F4-00

## Potrzeba

F1 = UTM Lock · F2 = Val gate · F3 = gdzie engage.  
F4 = **co** idzie na Blog: 1 ICP role / article, CTA Wizard `utm_source=blog`, tag `icp_role`.

| Amatorskie | Profesjonalne |
|------------|---------------|
| Ogólny AI blog „tips for business” | 1 role angle (installateur W1: bus 50m) |
| CTA w bio / offerte / multi-link | Exactly 1 Wizard UTM `blog` |
| Publish bez Val | Pipeline → F2 C.5 PASS → calendar bind |
| Auto-publish przed W3 | Draft only · publish via F2 gate (FROZEN) |

## Decyzja (1 path)

Deterministyczny `blog_pipeline` (templates ICP) + CLI + draft persist.  
LLM rewrite = later Wave3; DoD nie wymaga live Claude.

## Binary DoD

| # | DoD | Pass when |
|---|-----|-----------|
| D1 | role required | generate bez `icp_role` = FAIL |
| D2 | zakaz ogólnych | role=`general` / empty angle = FAIL |
| D3 | UTM blog | `utm_source=blog` + campaign `icp_{role}` |
| D4 | tag | caption/body zawiera `#role` lub `icp_role=` |
| D5 | Val C.5 | 1 article pipeline → PASS + pass_token |
| D6 | pytest | F1–F4 green |

## STOP

Auto-publish blog · Ads · VPS · spam engage · Wave3 cadence claim
