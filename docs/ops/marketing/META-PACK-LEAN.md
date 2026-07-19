---
status: "[ACTIVE]"
title: "META-PACK-01 Lean — Instant Form €10 + 1 Reel"
gate: "META-PACK-01"
campaign: "zzp_branding_check_v1"
updated: "2026-07-19"
---

# META-PACK-LEAN — max efekt / min złożoność

**Owner egzekucji:** Dowódca (Meta UI + WA).  
**Agent:** ten pack + HTML probe — **nie** klika Ads Manager i **nie** wydaje €.

Pełny playbook (3 kreacje, later): [FB-FIRST-CAMPAIGN.md](./FB-FIRST-CAMPAIGN.md).  
Start dnia: [OPERATOR-TODAY.md](./OPERATOR-TODAY.md).

## HTML probe (agent) — 2026-07-19

| Probe | Result |
|-------|--------|
| `https://zzpackage.flexgrafik.nl/wizard/` HTTP | **200** |
| `fbq` / Facebook pixel script | **PASS** |
| `fbevents` / `connect.facebook.net` | **PASS** |
| GTM (`GTM-` / `gtm.js`) | **FAIL / not found** in HTML snapshot (może iść innym torem — Events Manager i tak SoT) |

**HTML PASS ≠ Events Manager PASS.** Zanim wydasz €: Test Events `InitiateCheckout` + `Purchase` u Ciebie.

## Checklist 10 — gotowy do publish

| # | Check | Done |
|---|-------|------|
| 1 | Płatność Ads (iDEAL/karta) aktywna | [ ] |
| 2 | Page FlexGrafik + rola Ads admin | [ ] |
| 3 | Events Manager: Test `InitiateCheckout` widoczny | [ ] |
| 4 | Events Manager: Test `Purchase` widoczny | [ ] |
| 5 | Custom Audience klientów Wizard → **wykluczenie** | [ ] |
| 6 | Instant Form: Naam + WhatsApp + e-mail + vak | [ ] |
| 7 | Thank-you: Wizard UTM poniżej | [ ] |
| 8 | Drive `MKT/YYYY-WW/master_reel_9x16.mp4` (real bus) | [ ] |
| 9 | Kampania €10/dzień · 1 ad set · 1 ad (Reel) | [ ] |
| 10 | Publish → **zakaz edycji ad setu 7 dni** | [ ] |

## Struktura (lean v1)

```
Kampania: Lead Generation — zzp_branding_check_v1
├─ Budżet CBO/Advantage+: €10/dzień
├─ Lokalizacja konwersji: Instant Form
└─ Ad Set: NL ZZP Bouw/Techniek
   ├─ Advantage+ Audience: ON
   ├─ Geo: NL (nacisk Zuid-Holland + Noord-Brabant)
   ├─ Wiek: 25–55
   ├─ Wykluczenie: klienci Wizard
   └─ Ad (1): reel_a — przed/po bus 9:16
```

**Nie w v1:** karuzela, testimonial, TikTok, Sales objective, wiele ad setów.

## Instant Form (NL — wklej)

**Headline:** Gratis ZZP Branding Check — hoe herkenbaar is jouw bus?

**Intro:**  
Ben jij een ZZP'er in de bouw of techniek? In 2 minuten ontdek je hoeveel klanten jouw bus, kleding en bordje op de klus missen. Je krijgt direct een **persoonlijke check + een kortingscode** voor je ZZPackage.

**Pola:** Naam · Telefoon/WhatsApp · E-mail · Wat is je vak? (Installateur / Dakdekker / Schilder / Loodgieter / Elektricien / Hovenier / Anders) · opcjonalnie Plaats

**Thank-you:**  
✅ Bedankt! We sturen je check binnen 1 werkdag via WhatsApp.  
🔥 Start meteen: `https://zzpackage.flexgrafik.nl/wizard/?utm_source=meta&utm_medium=paid&utm_campaign=zzp_branding_check_v1&utm_content=form_thanks`  
🎁 Branding Game: `https://flexgrafik.nl/hoe-scoor-jij-je-branding/`  
📱 WhatsApp: +31 6 87286151  

Privacy: `flexgrafik.nl/privacybeleid/` + zgoda AVG.

## Creative — 1 Reel (`utm_content=reel_a`)

- Hook 0–3s: banalny bus → premium wrap  
- Prim: „Jouw bus rijdt 365 dagen langs je klanten. Staat jouw merk er echt op?”  
- Headline: Gratis ZZP Branding Check · CTA: Meer informatie  
- **Prawdziwy bus &gt; AI stock**

## Zakazy

- Edycja ad setu przez **7 dni**  
- Cel **Sales** / Purchase w Ads (miesiąc 2+)  
- Scale bez Purchase w pikselu (Events Manager)  
- Agent „PASS Meta” bez Twojego evidence

## Po publish

| Kiedy | Akcja |
|-------|--------|
| Każdy lead | WA &lt;15 min — [SPEED-TO-LEAD.md](./SPEED-TO-LEAD.md) |
| PON | [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md): spend, leads, CPL, wizard_starts, purchases |
| Po d7 | v1.1: 2. kreacja / organic Commander — nie wcześniej |

## Linki

- L0: [L0-INSTRUMENTATION.md](./L0-INSTRUMENTATION.md)  
- Unit economics: [UNIT-ECONOMICS.md](./UNIT-ECONOMICS.md)  
- Organic later: [Commander Marketing](https://api.zzpackage.flexgrafik.nl/commander/)  
- Pełny pack 3 kreacje: [FB-FIRST-CAMPAIGN.md](./FB-FIRST-CAMPAIGN.md)
