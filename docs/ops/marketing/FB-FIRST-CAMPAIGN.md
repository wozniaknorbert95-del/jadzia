---
status: "[ACTIVE]"
title: "FB Learning Campaign #1 — ZZP Branding Check"
campaign: "zzp_branding_check_v1"
updated: "2026-07-19"
source: "Ingest z docs/archive/marketing/2026-07-FlexGrafik_Pierwsza_Kampania_FB.md (FG-only)"
---

# Learning loop L1 — Instant Form (14 dni)

**Lean start (1 Reel, min złożoność):** [META-PACK-LEAN.md](./META-PACK-LEAN.md) — użyj tego do pierwszego publish; ten plik = pełny pack (3 kreacje) / v1.1.

Eksperyment, nie „kampania wizerunkowa”. Jedna zmienna: **creative**.  
Budżet learning: **€10/dzień**. Zakaz edycji struktury ad setu przez 7 dni.

Gate przed publish: [L0-INSTRUMENTATION.md](./L0-INSTRUMENTATION.md) musi być zielony (Pixel/CAPI + wykluczenia). Bez Purchase w pikselu → **nie** cel Sales.

## 0. Verify (15 min) — przed €

1. Ad Account + płatność (iDEAL/karta) aktywna.
2. Pixel + CAPI: `InitiateCheckout` / `Purchase` w Test Events na `zzpackage.flexgrafik.nl`.
3. Custom Audience klientów Wizard → **wykluczenie**.
4. Page role Ads admin + domena `flexgrafik.nl` zweryfikowana.

## 1. Cel = Leads (Instant Form)

| Cel | Werdykt |
|-----|---------|
| Leads Instant Form | **START** |
| Messaging → WhatsApp | Tylko jeśli budżet ≥ €15/dzień **i** L0 OK |
| Sales / Purchase | Miesiąc 2+ (gdy ≥50 Purchase/tydz. w danych) |
| Traffic / Awareness | **Pomiń** |

## 2. Struktura

```
Kampania: Lead Generation — zzp_branding_check_v1
├─ Budżet CBO/Advantage+: €10/dzień
├─ Lokalizacja konwersji: Instant Form
└─ Ad Set: NL ZZP Bouw/Techniek — check
   ├─ Advantage+ Audience: ON
   ├─ Geo: NL → nacisk Zuid-Holland + Noord-Brabant (po 7d: całe NL)
   ├─ Wiek: 25–55
   ├─ Wykluczenie: klienci Wizard
   └─ Ads (3):
        A reel_a — przed/po bus 9:16
        B car_b — karuzela 3 kroki
        C img_c — testimonial
```

## 3. Instant Form (NL — wklej)

**Headline:** Gratis ZZP Branding Check — hoe herkenbaar is jouw bus?

**Intro:**  
Ben jij een ZZP'er in de bouw of techniek? In 2 minuten ontdek je hoeveel klanten jouw bus, kleding en bordje op de klus missen. Je krijgt direct een **persoonlijke check + een kortingscode** voor je ZZPackage.

**Pola:** Naam · Telefoon/WhatsApp · E-mail · Wat is je vak? (Installateur / Dakdekker / Schilder / Loodgieter / Elektricien / Hovenier / Anders) · opcjonalnie Plaats

**Thank-you (conversion):**  
✅ Bedankt! We sturen je check binnen 1 werkdag via WhatsApp.  
🔥 Start meteen: `https://zzpackage.flexgrafik.nl/wizard/?utm_source=meta&utm_medium=paid&utm_campaign=zzp_branding_check_v1&utm_content=form_thanks`  
🎁 Branding Game: `https://flexgrafik.nl/hoe-scoor-jij-je-branding/`  
📱 WhatsApp: +31 6 87286151  

Wymagane: privacy `flexgrafik.nl/privacybeleid/` + zgoda AVG.

## 4. Kreacje (NL)

### A — Reel przed/po (`utm_content=reel_a`)
- Hook 0–3s: banalny bus → premium wrap  
- Prim: „Jouw bus rijdt 365 dagen langs je klanten. Staat jouw merk er echt op?”  
- Headline: Gratis ZZP Branding Check · CTA: Meer informatie  
- **Prawdziwe busy &gt; AI stock**

### B — Karuzela (`utm_content=car_b`)
- Karty: Wizard → iDEAL → 10 werkdagen  
- Prim: „Geen afspraak nodig. Geen verborgen kosten.”

### C — Testimonial (`utm_content=img_c`)
- Zdjęcie klient + bus  
- Prim: cytat installateur + „Doe de gratis check”

## 5. Kill / scale (OS)

Patrz [UNIT-ECONOMICS.md](./UNIT-ECONOMICS.md). Skrót po 7d / 14d:

| Wynik | Akcja |
|-------|-------|
| CPL &lt; €10 i Lead→Wizard ≥ 30% | Scale +€5/3d |
| CPL €10–20, Lead→Wizard ≥ 20% | Hold; kill najsłabszą kreację |
| Lead→Wizard &lt; 10% | Form/offer — nie scale |
| CPL &gt; €25 lub 0 leadów / 5d | Kill creative |

Po 14d (gdy działa): Lookalike z leadów · retarget InitiateCheckout · Sales objective dopiero przy danych Purchase.

## 6. Start 60 min

1. L0 verify  
2. Kampania Leads + Instant Form  
3. €10/dzień, Advantage+  
4. Audience + wykluczenia  
5. Form NL + privacy  
6. 3 kreacje z Asset Factory  
7. Publish → **nie edytuj 7 dni**  
8. PON: [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md)

## Status wykonania

| Step | Owner | Status |
|------|-------|--------|
| SoT playbook | agent | **DONE** (ten plik) |
| L0 verify w Events Manager | Dowódca | ready_for_human |
| Publish kampanii w Ads Manager | Dowódca | ready_for_human |
| Scorecard tydzień 1–2 | Dowódca | ready_for_human |
