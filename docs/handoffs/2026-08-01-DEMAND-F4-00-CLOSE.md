---
status: "[CLOSE · LOCAL]"
title: "DEMAND-F4-00 — Blog ICP pipeline"
updated: "2026-08-01"
gate: "DEMAND-OS-F4-00"
deploy_vps: false
---

# CLOSE — DEMAND-F4-00 (local)

## Analiza → decyzja

Nie budujemy „AI blog spam generator”. Budujemy **deterministyczny Blog ICP pipeline**: 1 role / article → UTM `blog` → Sniper Val C.5 → draft + calendar bind. Auto-publish = Wave3 / F2 gate (nadal FROZEN).

## Evidence

| Check | Result |
|-------|--------|
| pytest F1–F4 | **32 passed** |
| `f4 pipeline --role installateur` | **PASS** + `pass_token` |
| draft | `BLOG-DRAFTS/blog_w31_install_bus50m.{json,md}` |
| UTM | `utm_source=blog` · `utm_campaign=icp_installateur` |
| generic role | **FAIL** (`general` / empty) |
| Ads / VPS | untouched |

## Shipped

- `agent/demand_os/blog_pipeline.py`
- `tools/demand_os_f4.py` (`roles|generate|validate|pipeline|list`)
- `tests/test_demand_os_f4_blog.py`
- sample draft + calendar bind

## Next

`GO BUILD demand-f5` **blocked** do ≥2026-08-06 + GO Foundera (Ads).  
Albo Wave2 engage HITL na allowlist `active` (live comment nadal PARK bez env).  
Publish blog tylko przez F2 gate po świadomym HITL.
