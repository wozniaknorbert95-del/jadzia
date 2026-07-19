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
| 1 | Meta Pixel na zzpackage Wizard | Events Manager → Test Events przy starcie checkout | ready_for_human |
| 2 | Event `InitiateCheckout` | Test Events / debugger | ready_for_human |
| 3 | Event `Purchase` | Po test order / CAPI | ready_for_human |
| 4 | CAPI (server-side) jeśli używane | Events Manager match quality | ready_for_human |
| 5 | Pixel/domain `flexgrafik.nl` (opcjonalnie game) | Events Manager | ready_for_human |
| 6 | UTM taxonomy wdrożona w linkach | [CHANNEL-MATRIX.md](./CHANNEL-MATRIX.md) | **DONE** (SoT) |
| 7 | Custom Audience wykluczeń klientów | Ads Manager | ready_for_human |
| 8 | Domain verification flexgrafik.nl | Business Settings | ready_for_human |

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

**Uwaga:** HTML probe ≠ kompletne L0. **SoT verify zdarzeń** (`InitiateCheckout` / `Purchase`) = Events Manager Test Events — nadal **ready_for_human**.

## Gate

- L0 niepełne → learning Leads OK przy świadomości; **scale zabronione**  
- L0 zielone (Purchase widoczny) → wolno rozważać Sales objective później
