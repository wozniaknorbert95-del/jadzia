---
status: "[PARKED]"
title: "Meta „final” — unlock checklist (GTM G4 — po freeze)"
gate: "META-PACK-01"
updated: "2026-07-27"
parent: "GTM-1PAGER.md"
budget_freeze_until: "2026-08-06"
---

# Meta „final” — unlock checklist

> **PARK do 2026-08-06** — Dowódca: **zero budżetu paid 10 dni.** **Nie publish Ads. Nie €10/d.**

**Parent SoT:** [GTM-1PAGER.md](./GTM-1PAGER.md) · **Po freeze:** [META-PACK-LEAN.md](./META-PACK-LEAN.md) · [META-CLICK-PATH.md](./META-CLICK-PATH.md).

Po **2026-08-06**: odhacz poniżej → **„final”** → A1→A3 → publish €10/d → **7d hold ad set**.

---

## Pre-flight (L0 + infra)

| # | Check | Done | Ref |
|---|-------|------|-----|
| P1 | Płatność Ads (iDEAL/karta) aktywna | [ ] | META-PACK #1 |
| P2 | Page FlexGrafik + rola Ads admin | [ ] | META-PACK #2 |
| P3 | Events Manager: `InitiateCheckout` PASS | [x] | [L0-INSTRUMENTATION](./L0-INSTRUMENTATION.md) |
| P4 | Events Manager: `Purchase` — **PARK świadomie** (Mollie) | [ ] | akceptujesz learning bez Purchase scale |
| P5 | Custom Audience exclude klientów Wizard | [ ] | META-CLICK-PATH A1 |
| P0 | **Budget unlock ≥ 2026-08-06** | [ ] | Dowódca GO na spend |

## Offer + creative

| # | Check | Done | Ref |
|---|-------|------|-----|
| O1 | Instant Form NL (Naam + WA + email + vak) | [ ] | META-PACK #6 |
| O2 | Thank-you + Wizard UTM | [ ] | META-PACK #7 |
| O3 | `MKT/YYYY-WW/master_reel_9x16.mp4` real bus **lub** static fallback | [ ] | META-PACK #8 |
| O4 | Kampania €10/d · 1 ad set · 1 ad Reel | [ ] | META-PACK #9 |

## Publish + ops

| # | Check | Done | Ref |
|---|-------|------|-----|
| X1 | Publish w Ads Manager | [ ] | META-CLICK-PATH A3 |
| X2 | Zobowiązanie: **7 dni bez edycji ad setu** | [ ] | META-PACK #10 |
| X3 | WA skrypt gotowy · SLA &lt;15 min | [ ] | [SPEED-TO-LEAD](./SPEED-TO-LEAD.md) |
| X4 | PON scorecard reminder w kalendarzu | [ ] | [WEEKLY-SCORECARD](./WEEKLY-SCORECARD.md) |

---

## Teraz (freeze) — zamiast paid

| Akcja | Gdzie |
|-------|-------|
| Deploy VPS TT-PUB kod | Agent GO |
| FB organic HITL | Commander |
| TT token + E2E (HITL) | [FREE-TIKTOK](./FREE-TIKTOK.md) S6–S7 |
| Asset `MKT/YYYY-WW/` | Dowódca |

**Kampania (po freeze):** `zzp_branding_check_v1` · **€10/d** · camp ID `120254517992840360`
