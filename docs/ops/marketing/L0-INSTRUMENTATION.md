---
status: "[ACTIVE]"
title: "L0 Instrumentation — przed €"
gate: "MKT-INSTR-01"
updated: "2026-07-19"
---

# L0 — Instrumentacja (zakaz scale bez tego)

## Checklist

| # | Check | Jak | Status |
|---|-------|-----|--------|
| 1 | Meta Pixel na zzpackage Wizard | Events Manager → Test Events przy starcie checkout | **PASS** (2026-07-19) |
| 2 | Event `InitiateCheckout` | Test Events / debugger | **PASS** (2026-07-19) |
| 3 | Event `Purchase` | Po test order / CAPI | PARK — brak GO na live Mollie |
| 4 | CAPI (server-side) jeśli używane | Events Manager match quality | ready_for_human |
| 5 | Pixel/domain `flexgrafik.nl` (opcjonalnie game) | Events Manager | ready_for_human |
| 6 | UTM taxonomy wdrożona w linkach | [CHANNEL-MATRIX.md](./CHANNEL-MATRIX.md) | **DONE** (SoT) |
| 7 | Custom Audience wykluczeń klientów | Ads Manager | ready_for_human |
| 8 | Domain verification flexgrafik.nl | Business Settings | ready_for_human |

## Browser verify — 2026-07-19 (agent + Dowódca login)

| Field | Value |
|-------|--------|
| Pixel | **Piksel konta Norbert Woźniak** `1084197063740065` |
| Ad account | `758460034566524` |
| Test code | `TEST39712` |
| Domain | `zzpackage.flexgrafik.nl` |
| Evidence | Test Events: **Zainicjowanie przejścia do kasy** (= `InitiateCheckout`) · Przeglądarka · Ręczna konfiguracja · **15:24:32** · Przetworzono |
| Path | Wizard cart ≥€199 (F-001 + DF-006 = €218) → checkout step → `processCheckout` → `/afrekenen/` |
| Also seen | `PageView`, `SubscribedButtonClick` |
| Purchase | **PARK** — zatrzymano na Woo checkout; bez płatności Mollie |

## UTM (kanon)

```
utm_source=meta|tiktok|blog
utm_medium=paid|organic
utm_campaign=zzp_branding_check_v1
utm_content=reel_a|car_b|img_c|tt_hook|form_thanks|<blog_slug>
```

## Agent probe (HTML) — 2026-07-19

| Probe | Result |
|-------|--------|
| `https://zzpackage.flexgrafik.nl/wizard/` HTTP | **200** |
| `fbq` / `fbevents` / GTM w HTML | **PASS** (fbq=true, fbevents=true, gtm=true) |

## Gate

- `InitiateCheckout` **PASS** → learning Leads OK przy świadomości  
- Pełne L0 (Purchase) nadal PARK bez test/sandbox charge lub jawnego GO  
- Scale / Sales objective dopiero gdy Purchase widoczny w Test Events
