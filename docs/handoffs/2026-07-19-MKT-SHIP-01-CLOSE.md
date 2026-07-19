---
status: "[ACTIVE]"
title: "MKT-SHIP-01 — Operator ship CLOSE"
gate: "MKT-SHIP-01"
updated: "2026-07-19"
result: "PASS"
active_gate_next: "ready_for_human Meta pack (OPERATOR-TODAY #1–4)"
---

# MKT-SHIP-01 — CLOSE

## DONE (agent)

| Krok | Evidence |
|------|----------|
| Git hygiene jadzia | tip `3e60437` (UX strip od `c874999`) · origin synced |
| Deploy jadzia VPS | `/opt/jadzia` `3e60437` · `systemctl active` · health OK · `Organic HITL` + `mkt-os-strip` w `commander-ui` |
| Blog seed Cyber-Folks | `wp eval-file system/maintenance/seed-zzp-blog-posts.php` · post created · **HTTP 200** `https://zzpackage.flexgrafik.nl/blog/zzp-bus-belettering-herkenbaar/` |
| VCMS knowledge | handbook Scenariusz 3 Marketing OS · study-index · surfaces pointer · PR [#38](https://github.com/wozniaknorbert95-del/Flex-vcms/pull/38) · tip `29d4e87` · Deploy-VPS Integrity PASS |
| services | **nietknięte** (dirty media poza zakresem) |

## ready_for_human — Meta pack (OPERATOR-TODAY #1–4)

Agent **nie** loguje się w Ads Manager / Events Manager. Zrób po kolei:

| # | Zrób | Gdzie | Paste / link |
|---|------|-------|----------------|
| 1 | Test Events: `InitiateCheckout` + `Purchase` | Meta Events Manager → piksel zzpackage | [L0-INSTRUMENTATION.md](../ops/marketing/L0-INSTRUMENTATION.md) |
| 2 | Custom Audience klientów Wizard → **wykluczenie** | Ads Manager | [FB-FIRST-CAMPAIGN.md](../ops/marketing/FB-FIRST-CAMPAIGN.md) §0 / §2 |
| 3 | Folder `MKT/YYYY-WW/` + master Reel (lub reuse) | Google Drive COI-Marketing | [ASSET-FACTORY.md](../ops/marketing/ASSET-FACTORY.md) |
| 4 | Kampania Leads Instant Form **€10/dzień**, 3 kreacje | Ads Manager | Paste poniżej + pełny pack w FB-FIRST |

**#5 organic** (Commander Marketing) — UI strip już LIVE; drop gdy masz media z #3.

### Paste pack (skrót z FB-FIRST)

- **Kampania:** Lead Generation — `zzp_branding_check_v1` · CBO/Advantage+ **€10/dzień** · Instant Form  
- **Geo:** NL (Zuid-Holland + Noord-Brabant) · wiek 25–55 · wykluczenie klientów Wizard  
- **Form headline:** `Gratis ZZP Branding Check — hoe herkenbaar is jouw bus?`  
- **Thank-you Wizard:** `https://zzpackage.flexgrafik.nl/wizard/?utm_source=meta&utm_medium=paid&utm_campaign=zzp_branding_check_v1&utm_content=form_thanks`  
- **Zakaz:** edycja ad setu 7 dni · cel Sales · wiele ad setów · scale bez Purchase w pikselu  

Pełny NL form + 3 kreacje: [FB-FIRST-CAMPAIGN.md](../ops/marketing/FB-FIRST-CAMPAIGN.md)  
START dnia: [OPERATOR-TODAY.md](../ops/marketing/OPERATOR-TODAY.md)

## PARK

Gate D · Mollie LIVE · Ads API · TikTok API · QF w jadzia · dirty services media · scale paid bez L0 Events Manager.

## Next

`/vibe-init` → Dowódca Meta pack #1–4 → potem scorecard PON / organic #5.
