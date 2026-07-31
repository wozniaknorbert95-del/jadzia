---
status: "[CLOSED]"
title: "GTM-1PAGER CLOSE v2 — expert review + stack sync"
updated: "2026-07-27"
gate: "GTM-1PAGER"
---

# Handoff — 2026-07-27 GTM-1PAGER (v2 expert)

## DONE

### GTM core (v2 expert review)

[`docs/ops/marketing/GTM-1PAGER.md`](../ops/marketing/GTM-1PAGER.md) — rozszerzony SoT:

- Executive summary + messaging pillars (NL)
- **Conversion path z WA bridge** (Check → WA &lt;15 min → Wizard) — brakujący element v1
- Channel strategy matrix (paid / organic / TT / blog)
- KPI split: meta paid · meta organic · tiktok · anti-metrics
- **Definition of „final”** + TT activation gate (G0–G5)
- Budget guardrails + review cadence + anti-goals

### Nowy artefakt exec

[`docs/ops/marketing/META-FINAL-CHECKLIST.md`](../ops/marketing/META-FINAL-CHECKLIST.md) — unlock G1 dla Dowódcy (P/O/X checklist).

### Stack sync (12 plików)

| Plik | Zmiana |
|------|--------|
| OPERATOR-TODAY | META-FINAL-CHECKLIST · definicja „final” |
| META-PACK-LEAN | link GTM + META-FINAL |
| META-CLICK-PATH | prerequisite GTM/final |
| PLAN-14D | €5→€10 · GTM lock · Tor A NEXT |
| WEEKLY-SCORECARD | wizard_starts split paid/organic/tiktok |
| CHANNEL-MATRIX | parent GTM |
| FREE-TIKTOK · TIKTOK-ORGANIC | kanał #2 + KPI lock |
| UNIT-ECONOMICS · L0 · SPEED-TO-LEAD | parent GTM |
| MKT-BRAIN-PRO | H-Meta → publish €10 pending final |
| marketing/README | META-FINAL link |
| todo.json | GTM completed · META-FINAL pending |

## Expert verdict (v1 → v2)

| Obszar | v1 | v2 fix |
|--------|-----|--------|
| Conversion | Check → Wizard (skip WA) | **WA &lt;15 min** jako obowiązkowy most |
| „Final” | niezdefiniowane | META-FINAL-CHECKLIST + 3 warunki |
| TT start | „po Meta+cadence” vague | **TT activation gate** (3 checkboxy) |
| KPI organic | brak | meta organic secondary + TT primary metric |
| Budget | €10 bez ceiling rules | learning cap + scale/kill table |
| Cross-docs | 4 pliki | **12 plików** zsynchronizowanych |

## Decyzja GTM (bez zmian merytorycznych)

- Primary: **Meta paid learning** €10/d
- Secondary: **TikTok organic** po Meta + cadence
- TT success: **`wizard_starts` utm=tiktok**

## NEXT (Dowódca)

1. Odhacz [META-FINAL-CHECKLIST](../ops/marketing/META-FINAL-CHECKLIST.md)
2. Powiedz **„final”**
3. [META-CLICK-PATH](../ops/marketing/META-CLICK-PATH.md) A1→A3 → publish → 7d hold
4. PON: [WEEKLY-SCORECARD](../ops/marketing/WEEKLY-SCORECARD.md)

## STOP

Studio spam · Ads API · Mollie LIVE · deploy bez GO · commit bez prośby.

## Git

Dirty: GTM v2 + META-FINAL + stack sync + prior TT-PUB uncommitted. **No commit** unless Dowódca asks.
