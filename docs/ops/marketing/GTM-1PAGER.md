---
status: "[ACTIVE]"
title: "GTM 1-Pager — FlexGrafik SoT"
gate: "GTM-1PAGER"
updated: "2026-07-27 (budget freeze 10d · deploy · no paid Meta)"
approved: "2026-07-27 — Dowódca: zero ad spend do 2026-08-06"
budget_freeze_until: "2026-08-06"
---

# GTM 1-Pager — FlexGrafik

**SoT strategii demand.** Jedna strona: kto · co obiecujemy · jak sprzedajemy · który kanał teraz · jak mierzymy sukces.  
**Parent docs:** [META-PACK-LEAN](./META-PACK-LEAN.md) · [CHANNEL-MATRIX](./CHANNEL-MATRIX.md) · [UNIT-ECONOMICS](./UNIT-ECONOMICS.md) · [L0-INSTRUMENTATION](./L0-INSTRUMENTATION.md).

---

## Executive summary

> **BUDGET FREEZE (2026-07-27 → 2026-08-06):** **zero wydatków paid Meta.** Kampania €10/d **NIE startuje**. Tor = deploy + organic free (FB + TT).

| | |
|--|--|
| **Rynek** | NL · ZZP bouw/techniek · bus = billboard 365 dni |
| **Produkt** | ZZPackage via **Wizard-only** (≥ €199 checkout, typ. ~€218) |
| **Wejście** | Gratis ZZP Branding Check (lead) → WA &lt;15 min → Wizard |
| **Kanał #1 teraz (freeze)** | **FB organic** Commander HITL + **TT organic** prep/E2E — **$0** |
| **Kanał paid** | Meta €10/d — **PARK do 2026-08-06** · potem META-FINAL |
| **North Star** | `CPA_wizard` &lt; 40% marży · TT success = `wizard_starts` utm=tiktok |

---

## ICP

| Pole | Definicja |
|------|-----------|
| **Kto** | ZZP'er NL w **bouw of techniek** — installateur, dakdekker, schilder, loodgieter, elektricien, hovenier, overig |
| **Wiek** | 25–55 |
| **Geo** | NL — priorytet **Zuid-Holland + Noord-Brabant** (Advantage+ reszta NL OK) |
| **Job-to-be-done** | „Klanten moeten mijn bedrijf herkennen op de klus” — bus, kleding, bord |
| **Trigger** | Nieuwe bus · rebrand · concurrent met sterke wrap · klant vroeg „wie ben jij?” |
| **Wykluczenie** | Bestaande Wizard-klanten (`zzp_clients_exclude_v1` w Ads) |
| **Nie ICP** | IG creators, B2B wholesale, particulier zonder KvK, buiten NL, „alleen goedkoopste sticker” |

**Dowód z rynku (copy SoT):** pola vak + intro Instant Form w [META-PACK-LEAN](./META-PACK-LEAN.md).

---

## Positioning

**1 zdanie (NL, klient-facing):**  
*FlexGrafik maakt ZZP'ers in bouw en techniek zichtbaar op straat — van gratis branding check tot je ZZPackage in de Wizard.*

**Operator lock (PL):** Wizard-only cash path. Lead ≠ revenue. Views ≠ success. Agent nie wydaje € ani nie publikuje Ads.

### Messaging pillars (NL — spójne we wszystkich cutach)

1. **Herkenbaarheid** — „365 dagen langs je klanten — staat jouw merk erop?”  
2. **ZZP-specifiek** — bouw/techniek, geen generieke marketingbureau-taal  
3. **Laagdrempelig** — gratis check + kortingscode, daarna Wizard (geen klassieke webshop)

---

## Offer ladder + conversion path

```
AWARENESS          LEAD (Check)         NURTURE              INTENT              CASH
Reel / organic  →  Instant Form     →  WA <15 min      →  Wizard + UTM    →  Checkout
Meta paid €10       / FB CTA              + check 1d            InitiateCheckout      ≥€199
                    / TT bio+comment      [SPEED-TO-LEAD]       (L0 PASS)            (Purchase PARK)
```

| Stopień | Surface | CTA / UTM | Owner | L0 |
|---------|---------|-----------|-------|-----|
| **Check** | Meta Instant Form · FB organic · TT first-comment | `utm_campaign=zzp_branding_check_v1` | Dowódca · Commander HITL | leads (manual) |
| **Nurture** | WhatsApp + opcjonalnie Branding Game | Wizard link z UTM w WA | Dowódca · [SPEED-TO-LEAD](./SPEED-TO-LEAD.md) | SLA &lt;15 min |
| **Wizard** | `zzpackage.flexgrafik.nl/wizard/` | `utm_source=meta\|tiktok` · `medium=paid\|organic` | Product (zzpackage) | **IC PASS** |
| **Checkout** | `/afrekenen/` | Pixel events | Dowódca | Purchase **PARK** (Mollie) |

**Asset rule:** 1 master Reel/tydz. (`MKT/YYYY-WW/`) → cuts per [CHANNEL-MATRIX](./CHANNEL-MATRIX.md). Hypoteza w `NOTES.md` — nie nowa strategia per kanał.

### Canonical UTM (Wizard)

| Surface | Link |
|---------|------|
| Meta paid thank-you | `…/wizard/?utm_source=meta&utm_medium=paid&utm_campaign=zzp_branding_check_v1&utm_content=form_thanks` |
| Meta paid reel | `…&utm_content=reel_a` |
| Meta organic | `…&utm_source=meta&utm_medium=organic&utm_content=reel_a` |
| TikTok | `…&utm_source=tiktok&utm_medium=organic&utm_content=tt_hook` |

---

## Channel strategy (budget freeze aktywny)

> **2026-07-27 → 2026-08-06:** paid Meta **OFF**. Organic **$0** tory = priorytet.

| Kanał | Rola (freeze) | Status | KPI primary |
|-------|---------------|--------|-------------|
| **Meta paid** | money path (później) | **PARK** · €0 do 2026-08-06 | — wyłączone |
| **FB organic** | **#1 teraz** · compound | FREE-META **9/10** · Commander HITL | wizard_starts utm=meta organic |
| **TikTok organic** | **#2 teraz** · ten sam hook | deploy → token/E2E | **wizard_starts utm=tiktok** |
| **Blog ZZP** | SEO (później) | PARK | wizard_starts utm=blog |
| **IG** | — | out of scope | — |

**Po freeze:** Meta paid wraca jako #1 money · [META-FINAL-CHECKLIST](./META-FINAL-CHECKLIST.md).

---

## KPI framework

### North Star (paid scale gate)

`CPA_wizard < 0.40 × marża_brutto_ZZPackage` — [UNIT-ECONOMICS](./UNIT-ECONOMICS.md).  
**Bez Purchase w pikselu → zakaz scale budżetu** (learning ≤ €10/d OK).

### Meta paid — **PARK do 2026-08-06** (freeze)

Brak spend · brak scorecard paid · nie wypełniaj CPL/CPA w freeze.

### Meta organic

| Metryka | Uwaga |
|---------|-------|
| `wizard_starts` utm=meta organic | secondary — nie steruje paid budget |
| ER / reach (DTL) | baseline compound — nie North Star |

### TikTok — success ≠ views

| Metryka | Definicja |
|---------|-----------|
| **TT success** | **`wizard_starts` WHERE `utm_source=tiktok`** |
| **TT leading** | first-comment / bio click → Wizard (verified: brak Website w profile) |
| **Nie KPI** | views · followers · likes · reach bez wizard_starts |
| **Cadence** | 2–3×/tydz. po TT-PUB E2E · cut `tt_hook_15s` — **primary KPI w freeze** |

### Anti-metrics (globalnie)

Followers · likes · reach · video views · „viral” bez `wizard_starts` / `purchases` — **nie uzasadniają budżetu ani gate PASS**.

---

## Execution sequence + gates

| # | Gate | Owner | Done when |
|---|------|-------|-----------|
| **G0** | GTM lock | Agent | **DONE** — ten dokument |
| **G1** | Meta **„final”** | Dowódca | **PARK do 2026-08-06** — budget freeze · zero paid |
| **G1b** | **Deploy VPS** + TT-PUB kod | Agent | tip `4cf66fe+` · health OK |
| **G2** | Asset cadence organic | Dowódca + Commander | `MKT/YYYY-WW/` · FB + TT hook |
| **G3** | TT-PUB E2E | Dowódca + Agent | token + calendar publish (S6–S7) |
| **G4** | Meta paid publish | Dowódca | **po 2026-08-06** · checklist + €10/d |

### Co znaczy „final” (unlock Meta publish)

**PARK do 2026-08-06** — Dowódca zablokował paid (brak budżetu 10 dni). **Nie publish Ads.**

Po **2026-08-06** — odhacz [META-FINAL-CHECKLIST](./META-FINAL-CHECKLIST.md) → powiedz **„final”** → A1–A3 → €10/d.

### TT activation gate (kiedy organic TT aktywny)

- [ ] VPS deploy TT-PUB kod (G1b)  
- [ ] G2: min. 1× master asset w `MKT/YYYY-WW/`  
- [ ] Dowódca GO: `TIKTOK_ACCESS_TOKEN` + verified URL (S6) → E2E (S7)  

**Nie wymaga Meta paid** — TT organic = $0 tor równoległy w freeze.

---

## Budget guardrails

| Faza | Budżet | Reguła |
|------|--------|--------|
| **Freeze (do 2026-08-06)** | **€0 paid** | Ads OFF · organic only |
| Learning v1 (po freeze) | **€10/d** CBO | 1 kampania · 1 ad set · 1 ad |
| Scale (po proof) | +€5 / 3 dni | tylko gdy CPL &lt;€10 **i** Lead→Wizard ≥30% |
| Kill | — | CPL &gt;€25 **lub** 0 leadów / 5d **lub** Lead→Wizard &lt;10% |
| Ceiling bez Purchase | ≤ €10/d | nie podnosimy bez Purchase w Events Manager |

---

## Review cadence

| Kiedy | Co | Gdzie |
|-------|-----|-------|
| Każdy lead | WA &lt;15 min | [SPEED-TO-LEAD](./SPEED-TO-LEAD.md) |
| PON | Scorecard + jedna decyzja HOLD/KILL/SCALE | [WEEKLY-SCORECARD](./WEEKLY-SCORECARD.md) |
| Po d7 learning | v1.1: 2. kreacja **lub** organic boost — nie wcześniej | META-PACK-LEAN |
| MB propose | Observe · APPROVE = ticket — **nie** Ads create | [OPERATOR-TODAY](./OPERATOR-TODAY.md) |

---

## Anti-goals (nie robimy)

- Osobna „TikTok strategy” odcięta od master assetu  
- IG / dual-publish / RPA DM  
- Sales objective w Meta v1 · karuzela · multi ad set  
- Scale paid bez L0 IC + bez Lead→Wizard evidence  
- Mollie LIVE / Purchase force bez GO  
- Agent „PASS Meta/TT” bez Dowódca evidence  

---

## STOP (twardy)

- Publish / scale paid Meta w freeze (do 2026-08-06)  
- Ads API create · TikTok Studio spam bez E2E · fake PASS · secrets w repo  
