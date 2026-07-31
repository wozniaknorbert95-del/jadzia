---
status: "[ACTIVE]"
title: "VHQ Decision Instrument Scorecard — DoD SoT"
updated: "2026-07-31"
program: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
research: "docs/handoffs/2026-07-31-VF-VHQ-DECISION-INSTRUMENT-RESEARCH.md"
baseline_post_w1: "2026-07-31 after VF-VHQ-P2-SNR-00 DEPLOY"
---

# VHQ Decision Instrument Scorecard

**Cel:** doprowadzić Virtual HQ od **command surface** do **decision instrument** — bez fake KPI, bez 3D-first, bez kłamstwa statusem.

**Zasada 100%:** każdy wymiar = **5/5** według binary DoD poniżej.  
Wymiary zależne od brakującego SoT (Order Desk) nie dostają fake PASS — zostają `blocked_sot` z checklistą.

---

## Scorecard (aktualny)

| ID | Wymiar | Target | Baseline (pre-W1) | Po P2-SNR W1 (prod) | Gate do 5/5 |
|----|--------|--------|-------------------|---------------------|-------------|
| S1 | Trust / honesty | 5 | 5 | **5** | Regression only |
| S2 | Escape / safety | 5 | 5 | **5** | Regression only |
| S3 | Approval discipline | 5 | 4.5 | **4.5** | `VF-VHQ-DI-S3-APPROVAL` |
| S4 | Signal-to-noise | 5 | 1.5 | **5** (S4 CLOSE 2026-07-31) | — |
| S5 | Ranked next action | 5 | 2 | **~2.5** | `VF-VHQ-DI-S5-NBA` ← ACTIVE |
| S6 | Money/risk narrative | 5 | 2 | **2** | `VF-VHQ-DI-S6-MONEY` |
| S7 | Closed commercial loop | 5 | 1.5 | **1.5** | `VF-VHQ-DI-S7-LOOP` (needs Order SoT) |
| S8 | ≤30s decision quality | 5 | 2.5 | **~3.6** | Composite — closes when S4–S6 PASS |

**Prod S4 evidence:** Decide-now = 2 ACTION (fb_post + sales_cta); **no** analytics_stale; stubs 0%; noise 0%; Ops confidence degraded (not fire). Tip `c56b13e` · `?v=vhq-w62a`

---

## Binary DoD per dimension (must all be true for 5/5)

### S1 Trust / honesty — **PASS maintain**

- [x] Statusy LIVE/PARTIAL/UNVERIFIED/PARKED + evidence ID  
- [x] No fake Order LIVE (EV-W2-010)  
- [ ] **Regression gate:** every DI gate dogfood re-checks Order PARKED + no invented KPI  

**FAIL if:** any room shows LIVE without evidence ID.

### S2 Escape / safety — **PASS maintain**

- [x] Esc: room → MC → Console  
- [x] Sign in never blocked  
- [ ] **Regression:** Esc ladder in each DI gate dogfood  

### S3 Approval discipline — target 5

| # | DoD |
|---|-----|
| S3.1 | L2 companion approve leaves UI consistent with parent state (no silent lie) OR honest PARTIAL banner with evidence ID |
| S3.2 | L3/L4: 0 Approve buttons; STOP copy visible |
| S3.3 | Vault strip: pending count matches typed bus; CTA opens Vault |
| S3.4 | Unit/API tests for L2/L3 matrix green |

**STOP:** no silent L3 execute · no Ads/Mollie from Approve.

### S4 Signal-to-noise — target 5 (finish after W1)

| # | DoD | Status |
|---|-----|--------|
| S4.1 | Decide-now contamination by stubs = **0%** | DONE |
| S4.2 | Chronic freshness/GA4 never sole Ops UWAGA | DONE |
| S4.3 | `analytics_stale` not in Decide-now CRITICAL/ACTION (INFO hygiene) | DONE |
| S4.4 | Noise ratio non-actionable / Decide-now **&lt;10%** | DONE (0%) |
| S4.5 | pytest + prod JWT dogfood evidence | DONE (`evidence-vhq-di-s4/`) |

### S5 Ranked next action (NBA) — target 5

| # | DoD |
|---|-----|
| S5.1 | Exactly **1** primary “Director: do this now” card on MC L1 (others secondary) |
| S5.2 | Deterministic score: money × urgency × risk − uncertainty (no ML black-box) |
| S5.3 | Card fields: why-now · evidence+ts · owner · one CTA · cost of inaction · L1/L2/L3 class |
| S5.4 | Cold-open dogfood: Founder names Q3+Q6 correctly in ≤30s (≥90% runs) |
| S5.5 | Unit tests for ranking eligibility + order |

### S6 Money/risk narrative — target 5

| # | DoD |
|---|-----|
| S6.1 | Q1 answers from **real** Wizard/lead/quote signals (or honest `insufficient_data` + one verify CTA) |
| S6.2 | No vanity totals; no fake € green |
| S6.3 | Top risk blocker named with owner when present |
| S6.4 | Dogfood screenshot + event IDs |

### S7 Closed commercial loop — target 5

| # | DoD |
|---|-----|
| S7.0 | **Prerequisite:** Order Desk SoT exists (unpark EV-W2-010 with evidence) — else status `blocked_sot` |
| S7.1 | Event contract: quote → order → production → payment/result |
| S7.2 | Quote-to-paid + exception cards measurable |
| S7.3 | Mollie LIVE only with separate Founder GO |

Until S7.0: max honest score **2/5** (Sales→Wizard MVP loop only). Document as `partial_loop` not FAIL honesty.

### S8 ≤30s decision quality — target 5

Closes automatically when **S4≥5 ∧ S5≥5 ∧ S6≥5** and dogfood timer ≤30s with correct Q3+Q6.  
Also requires S1+S2 regression green.

---

## Gate order (1-1-1, no mega-diff)

```text
S4-SNR-FINISH → S5-NBA → S6-MONEY → S3-APPROVAL → S8 verify composite
S7-LOOP only after Order SoT GO (blocked_sot until then)
```

Hard STOP across all gates: no 3D unpark · no Ads until freeze · no fake LIVE · no MKT staging · deploy only with GO DEPLOY.

---

## Agent closeout contract

Each gate MUST:

1. BLAST + binary DoD from this scorecard  
2. Tests first (or with code) for policy/rank changes  
3. `/jadzia-test` scoped green  
4. `/post-coding` → push → deploy only with GO  
5. Prod dogfood evidence updating this scorecard row  
6. CLOSE handoff + todo tip sync  

Workflow: `.agents/workflows/vhq-decision-instrument.md`
