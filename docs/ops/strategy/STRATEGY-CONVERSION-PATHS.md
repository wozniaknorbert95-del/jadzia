---
status: "[SUPERSEDED]"
title: "Ścieżki konwersji FlexGrafik"
updated: "2026-07-31"
superseded_by: "docs/ops/strategy/STRATEGY-PACK.md#ch4--conversion"
---

> **SUPERSEDED — nie SoT.** Kanon: [`STRATEGY-PACK.md`](./STRATEGY-PACK.md) (Ch4 CONVERSION). Index: [`README.md`](./README.md).

# STRATEGY CONVERSION PATHS

Każda ścieżka: **entry → trust → CTA → friction → paid → proof→Growth**.  
Cash koniec zawsze = **Wizard paid**.

## Path 1 — TikTok → app/portal → Wizard → paid

```mermaid
flowchart LR
  TT[TikTok_UTM] --> Land[app_or_portal]
  Land --> Trust[Game_or_portfolio]
  Trust --> CTA[Wizard_CTA]
  CTA --> Pay[Paid]
  Pay --> Proof[Asset_back_to_TT]
```

| | AS-IS | TO-BE strategiczne |
|--|-------|-------------------|
| Entry | rytm TT słaby | ≥3/tydz. Agent_TT |
| Friction | brak UTM dyscypliny | UTM Lock obowiązkowy |
| KPI | starts `utm_source=tiktok` · paid |

## Path 2 — TikTok → Wizard direct

```mermaid
flowchart LR
  TT[TikTok_UTM] --> Wiz[Wizard]
  Wiz --> Pay[Paid]
```

| | AS-IS | TO-BE |
|--|-------|-------|
| Friction | słaby mockup-before-pay | Design proof w creatives + later CRE mockup |
| KPI | direct starts · paid |

## Path 3 — Blog SEO → Wizard

```mermaid
flowchart LR
  SEO[Google_query] --> Blog[Blog_post]
  Blog --> Edu[Trust_edu]
  Edu --> CTA[Wizard_CTA_UTM]
  CTA --> Pay[Paid]
```

| | AS-IS | TO-BE |
|--|-------|-------|
| Entry | ~kilka postów | 1/tydz. + CTA zawsze |
| KPI | organic→starts |

## Path 4 — Design Agent → offerte/WA → Wizard (NIE omijać)

```mermaid
flowchart LR
  DA[Design_Agent] --> Mock[AI_mockups]
  Mock --> Lead[Lead_captured]
  Lead --> Score[Lead_score]
  Score --> STL[WA_or_Widget_15min]
  STL --> Wiz[Wizard_with_context]
  Wiz --> Pay[Paid]
```

| | AS-IS | TO-BE |
|--|-------|-------|
| Luka | offerte 48h jak osobny koniec | Wizard = obowiązkowy next step |
| KPI | DA→Wizard <24h · paid |

## Path 5 — Gra → coupon → Wizard

```mermaid
flowchart LR
  Game[app_game] --> Coup[Coupon_GAME10]
  Coup --> Wiz[Wizard_coupon_URL]
  Wiz --> Pay[Paid]
```

| | AS-IS | TO-BE |
|--|-------|-------|
| Bridge | istnieje | każdy growth CTA co 2. TT |
| KPI | coupon redemption · paid |

## Path 6 — Widget / COM-AI → Wizard

```mermaid
flowchart LR
  Wid[Widget_AI_disclosure] --> Intent[Intent_qualify]
  Intent --> CTA[Wizard_deeplink]
  CTA --> Pay[Paid]
```

| | AS-IS | TO-BE |
|--|-------|-------|
| Luka | martwy bez ruchu | karmiony Path 1–3 |
| KPI | CTA click · paid |

## Path 7 — Google brand/review → portal → Wizard

```mermaid
flowchart LR
  G[Google_SERP_or_Review] --> Portal[flexgrafik_nl]
  Portal --> CTA[Wizard]
  CTA --> Pay[Paid]
```

| | AS-IS | TO-BE |
|--|-------|-------|
| Trust | 6 reviews | volume reviews + spójny FAQ |
| KPI | brand clicks → starts |

## Path 8 — CS / referral → Wizard

```mermaid
flowchart LR
  Ship[Delivered] --> CS[CS_Dplus3]
  CS --> Ask[Review_plus_referral]
  Ask --> Wiz[Wizard_UTM_referral]
  Wiz --> Pay[Paid]
```

| | AS-IS | TO-BE |
|--|-------|-------|
| Luka | CS manual rzadki | obowiązek D+3 + zgoda case |
| KPI | referral starts · reviews |

## Friction map (global)

```mermaid
flowchart TD
  G1[Brak_rytmu_uwagi] --> G3[STL_opoznione]
  G3 --> G4[Wizard_bez_wow]
  G4 --> G5[UTM_dziura]
  G5 --> G6[GateD_PARK]
  G6 --> G7[Ops_desk_PARK]
```

Naprawa strategiczna kolejność = G1→G3→G5→G4→G6(GO)→G7(GO) — zgodna z AS-IS mapą działów.

## KPI konwersji (pack)

| Funnel stage | Metryka |
|--------------|---------|
| Attention | publish · impressions proxy |
| Landing | CTR UTM |
| Start | Wizard starts |
| Pay | paid real ≥€199 |
| Loop | proof reused in TT/blog |

## ACCEPT

`ACCEPT FLEXGRAFIK STRATEGY PACK`
