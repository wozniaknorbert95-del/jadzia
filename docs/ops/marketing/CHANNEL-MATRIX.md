---
status: "[ACTIVE]"
title: "Marketing OS — Channel Matrix + UTM"
updated: "2026-07-27 (GTM lock)"
parent: "GTM-1PAGER.md"
---

# Channel Matrix — 1 asset → N surfaces

**GTM:** [GTM-1PAGER.md](./GTM-1PAGER.md) — jeden master, wiele cutów, ten sam offer ladder.

## Zasada

Jeden **master asset** (Reel przed/po 9:16) w tygodniu ISO (`MKT/YYYY-WW/`).  
Każdy kanał = cut + CTA Wizard, nie osobna „strategia kreatywna”.

| Surface | Cut | utm_source | utm_medium | CTA |
|---------|-----|------------|------------|-----|
| Meta Ads (paid) | 9:16 + 1:1 | `meta` | `paid` | Instant Form → thank-you → Wizard |
| FB organic (Commander HITL) | ten sam master | `meta` | `organic` | Wizard / WA |
| TikTok organic (`@flexgrafik.nl`) | 15s hook z mastera | `tiktok` | `organic` | bio → Wizard |
| ~~IG organic~~ | — | — | — | **out of scope** (brak konta) |
| Blog ZZP | stills z mastera | `blog` | `organic` | in-content → Wizard |
| Retarget (później) | ten sam Reel | `meta` | `paid` | Wizard + game code |

## UTM taxonomy (sztywna)

```
utm_source   = meta | tiktok | blog
utm_medium   = paid | organic
utm_campaign = zzp_branding_check_v1   # bump _v2 przy nowym eksperymencie
utm_content  = reel_a | car_b | img_c | tt_hook | blog_slug
```

Przykład Wizard link (thank-you / bio / blog):

```
https://zzpackage.flexgrafik.nl/wizard/?utm_source=meta&utm_medium=paid&utm_campaign=zzp_branding_check_v1&utm_content=reel_a
```

## GDrive SoT folder

```
MKT/
  YYYY-WW/
    master_reel_9x16.mp4
    feed_1x1.mp4
    carousel_1.png … carousel_3.png
    testimonial.jpg
    tt_hook_15s.mp4
    NOTES.md          # UTM, CTA, hipoteza
```

Commander / GDrive marketing folder — ten sam WW przy publish HITL.
