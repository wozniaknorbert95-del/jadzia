---
status: "[ACTIVE]"
title: "GTM 1-Pager — FlexGrafik SoT"
gate: "GTM-1PAGER"
updated: "2026-07-27 (expert review v2)"
approved: "2026-07-27 — Dowódca decyzja A"
---

# GTM 1-Pager — FlexGrafik

**SoT strategii demand.** Jedna strona: kto · co obiecujemy · jak sprzedajemy · który kanał teraz · jak mierzymy sukces.  
**Parent docs:** [META-PACK-LEAN](./META-PACK-LEAN.md) · [CHANNEL-MATRIX](./CHANNEL-MATRIX.md) · [UNIT-ECONOMICS](./UNIT-ECONOMICS.md) · [L0-INSTRUMENTATION](./L0-INSTRUMENTATION.md).

---

## Executive summary

| | |
|--|--|
| **Rynek** | NL · ZZP bouw/techniek · bus = billboard 365 dni |
| **Produkt** | ZZPackage via **Wizard-only** (≥ €199 checkout, typ. ~€218) |
| **Wejście** | Gratis ZZP Branding Check (lead) → WA &lt;15 min → Wizard |
| **Kanał #1 teraz** | **Meta paid learning** €10/d · Instant Form · **po** Dowódca „final” |
| **Kanał #2** | TikTok organic — ten sam asset · **po** Meta publish + cadence |
| **North Star** | `CPA_wizard` &lt; 40% marży brutto · TT success = `wizard_starts` utm=tiktok |

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

## Channel strategy

| Kanał | Rola | Status | KPI primary |
|-------|------|--------|-------------|
| **Meta paid** | #1 money · learning | HOLD → **„final”** → publish €10/d | leads · CPL · Lead→Wizard · wizard_starts |
| **FB organic** | compound · trust · ten sam asset | FREE-META **9/10 CLOSED** | wizard_starts utm=meta organic · ER (DTL) |
| **TikTok organic** | #2 dystrybucja · ten sam hook | TT-PUB **5/7** · E2E po Meta+cadence | **wizard_starts utm=tiktok** |
| **Blog ZZP** | SEO compound (później) | PARK do triggerów | wizard_starts utm=blog |
| **IG** | — | **out of scope** | — |

### Dlaczego Meta paid przed TikTok

| Meta paid | TikTok organic |
|-----------|----------------|
| L0 InitiateCheckout **PASS** | Brak token VPS · brak E2E publish |
| Checklist + Instant Form gotowe | Kod 5/7 — nie prod-ready |
| Unit economics + CPL/CPA framework | Views nie korelują z Wizard |
| WA SLA już zdefiniowany | Aktywacja **po** Meta publish + 1× asset cadence |

**FB organic:** utrzymanie równoległe (Commander HITL), nie zastępuje paid learning w tygodniu 1–2.

---

## KPI framework

### North Star (paid scale gate)

`CPA_wizard < 0.40 × marża_brutto_ZZPackage` — [UNIT-ECONOMICS](./UNIT-ECONOMICS.md).  
**Bez Purchase w pikselu → zakaz scale budżetu** (learning ≤ €10/d OK).

### Meta paid — tygodniowo ([WEEKLY-SCORECARD](./WEEKLY-SCORECARD.md))

| Metryka | Definicja | Próg / akcja |
|---------|-----------|--------------|
| `spend` | EUR Ads Manager | cap learning **€10/d** |
| `leads` | Instant Form unikalne | 0 / 5d → kill creative |
| `CPL` | spend / leads | &gt; €25 → kill; &lt; €10 + L→W ≥30% → scale +€5/3d |
| `wizard_starts` | UTM meta + paid + campaign | razem z Lead→Wizard |
| `Lead→Wizard` | wizard_starts / leads | &lt; 10% → FORM/OFFER fix, nie scale |
| `purchases` | Pixel (gdy LIVE) | 0 po 14d + spend ≥€100 → nie scale |
| `SLA median` | min do pierwszego WA | cel **&lt;15 min** |

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
| **Cadence** | 2–3×/tydz. **po** TT-PUB E2E · cut `tt_hook_15s` |

### Anti-metrics (globalnie)

Followers · likes · reach · video views · „viral” bez `wizard_starts` / `purchases` — **nie uzasadniają budżetu ani gate PASS**.

---

## Execution sequence + gates

| # | Gate | Owner | Done when |
|---|------|-------|-----------|
| **G0** | GTM lock | Agent | **DONE** — ten dokument |
| **G1** | Meta **„final”** | Dowódca | Checklist 10 [META-PACK-LEAN](./META-PACK-LEAN.md) **lub** A1–A3 [META-CLICK-PATH](./META-CLICK-PATH.md) + publish €10/d |
| **G2** | Learning hold | Dowódca | **7 dni** bez edycji ad setu · każdy lead → WA &lt;15 min |
| **G3** | Asset cadence | Dowódca + Commander | `MKT/YYYY-WW/` master live · FB organic HITL |
| **G4** | TT-PUB E2E | Dowódca + Agent | [FREE-TIKTOK](./FREE-TIKTOK.md) S6 token + S7 calendar publish |
| **G5** | TT compound | Agent | TT-INS-01 · TT-CMT-01 (po G4) |

### Co znaczy „final” (unlock Meta publish)

Dowódca mówi **„final”** **dopiero gdy**:

1. [ ] Checklist 10 w META-PACK-LEAN odhaczony (min. #1–4 L0, #6–10 form+creative+publish plan)  
2. [ ] Świadoma decyzja: Purchase PARK OK na learning phase  
3. [ ] Gotowy real bus Reel w `MKT/YYYY-WW/` (#8) — **fallback static OK** per META-CLICK-PATH  

Po „final”: wykonaj [META-CLICK-PATH](./META-CLICK-PATH.md) A1→A3 · **7d hold** · PON scorecard.

### TT activation gate (kiedy #2 staje się aktywny)

**Wszystkie:**

- [ ] G1+G2: Meta opublikowane **lub** min. 1 tydzień learning rozpoczęty  
- [ ] G3: min. 1× master asset w `MKT/YYYY-WW/`  
- [ ] Dowódca GO na VPS token + deploy TT-PUB  

---

## Budget guardrails

| Faza | Budżet | Reguła |
|------|--------|--------|
| Learning v1 | **€10/d** CBO | 1 kampania · 1 ad set · 1 ad (`reel_a`) |
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

Ads API create · scale bez „final” · TikTok Studio spam bez E2E · fake PASS · deploy VPS bez GO (Zasada 11) · secrets w repo.
