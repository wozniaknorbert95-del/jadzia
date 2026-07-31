---
status: "[RESEARCH]"
title: "VHQ Decision Instrument — research pack for remediation plan"
updated: "2026-07-31"
gate_prep: "P2-SNR-00 / Decision Instrument remediation (not unlocked)"
inputs:
  - "docs/handoffs/2026-07-31-VF-VHQ-UX-AUDIT-00-EXPERT-VERIFY.md"
  - "docs/handoffs/2026-07-31-VF-VHQ-UX-AUDIT-00-REPORT.md"
  - "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md"
  - "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md"
staff:
  - "Human Factors / Mission Control UX"
  - "RevOps / Revenue Orchestration"
  - "SRE Alert Hygiene"
  - "Progressive Disclosure / Exec Dashboard UX"
runtime_changes: false
---

# Research pack — od command surface do decision instrument

**Cel dokumentu:** ułatwić napisanie profesjonalnego planu naprawczego.  
**Nie jest planem implementacji.** Nie odblokowuje gate’a. Zero kodu / deploy.

**Werdykt sztabu (jedna linia):**  
Najpierw **SNR + ranked Next Best Action (NBA)** na istniejącym MC; dopiero potem loop Sales→Wizard→(Order gdy SoT). 3D / nowe pokoje / fake KPI = anty-ROI.

---

## 0. Sztab i metody

| Rola | Wkład |
|------|--------|
| Human Factors / Mission Control | Command surface vs decision instrument; ≤30s; progressive disclosure |
| RevOps / Revenue Orchestration | NBA, money×risk scoring, MVP loop przy Order PARKED |
| SRE Alert Hygiene | Severity, burn-rate thinking, actionable % KPI, chronic ≠ page |
| Exec Dashboard UX (2025–26) | Glance → detail → config; 1–3 directives |
| VHQ audit SoT | E1 stubs · E2 freshness · EV-W2-010 · trust PASS |

Źródła zewnętrzne (wzorce, nie copy produktów):
- Alert fatigue / actionable alerts 2025 — [incident.io](https://incident.io/blog/alert-fatigue-solutions-for-dev-ops-teams-in-2025-what-works), observability burn-rate / persona dashboards — [CertVanta](https://certvanta.com/blog/2025/08/observability_that_reduces_pager_fatigue)
- Severity → escalation mapping — [SRE alerting practices](https://incident.io/blog/sre-alerting-best-practices)
- Progressive disclosure dashboards 2025–26 — [Pixxen](https://pixxen.com/blog/progressive-disclosure-saas/), [Tim Graf](https://timgraf.com/ui/the-architecture-of-complexity-mastering-progressive-disclosure-in-2026-saas-dashboard-design/)
- Revenue command / NBA patterns — RevOps command-center thesis (unified signals → ranked actions → approval → outcome), Gong-style monitor→activate→measure loop (inspiracja architektoniczna, nie feature parity)

Repo grounding: EXPERT-VERIFY E1–E5 · PROGRAM §1 · ARCH Q1–Q7.

---

## 1. Definicje operacyjne (checklist)

### Command surface (VHQ = PASS)

- Honest status + evidence ID  
- Escape / teleport / Sign in  
- Fail-closed L3/L4  
- No fake LIVE / no invented desks  

### Decision instrument (VHQ = NOT YET)

Musi spełniać **wszystkie**:

1. Separacja **Decide now** vs diagnostyka / hygiene  
2. Ranking: impact × urgency × reversibility × confidence — nie sama etykieta CRITICAL  
3. Każda top-karta: fakt · evidence+ts · freshness · owner · jedna akcja · koszt bezczynności · klasa L1/L2/L3  
4. Stub / chronic / ownerless **nie konkurują** z realnym ryzykiem  
5. First viewport: **1–3** dyrektywy (nie firehose)  
6. Po akcji: widoczny outcome (closed loop uczenia)  
7. Braki danych = Q7 honesty, nie permanentny P0  

---

## 2. Co branża uznaje za „naprawdę działa” (2024–2026)

### 2.1 Alert / signal hygiene (SRE → mapuj na Decision Rail)

| Zasada | Implikacja dla VHQ |
|--------|-------------------|
| If everything is critical, nothing is | CEO stub CRITICAL = defekt instrumentu |
| Alert tylko gdy **actionable** (impact + next step) | Karta bez owner/action/deadline → poza rail |
| Target **30–50%** alertów actionable; &lt;10% = kryzys szumu | Metryka noise ratio na CRITICAL surface |
| Chronic / always-on → dashboard chrome, nie page | Freshness/GA4 red → secondary confidence |
| Group symptoms → one incident | Dedup stubów / powtarzalnych symptomów |
| Severity maps to escalation (P0–P3) | CRITICAL ≡ wymaga decyzji teraz; reszta watch/queue |
| Symptom &gt; cause noise | Biznes: quote stuck / approval wait &gt; „GA4 red” |

### 2.2 Progressive disclosure (exec / ops dashboards)

Trzy warstwy (nie więcej na cold-open):

| Warstwa | Pytanie | VHQ target |
|---------|---------|------------|
| L1 Glance (&lt;3–10s) | OK / uwaga / decyzja? | 1 status strip + **1–3 Decide now** |
| L2 Explore | Dlaczego? | Queue, pulse, vault strip |
| L3 Config / deep | Jak naprawić SoT? | Operations Console, Audyt, settings |

Anti-pattern: wszystko na L1 (obecny MC pod time pressure).

### 2.3 Revenue command / Next Best Action

Działający NBA ≠ wykres. To **jedna karta play**:

- Co zrobić teraz (1 CTA)  
- Dlaczego teraz (2–3 dowody + freshness)  
- Wynik biznesowy / koszt zwłoki  
- Klasa approval (L1 wykonaj / L2 stamp / L3 STOP)  
- Jak zmierzymy efekt po wykonaniu  

Pętla: **Monitor → Rank → Act (HITL) → Measure outcome → popraw regułę.**  
Bez outcome taxonomy instrument się nie uczy — buduje tylko szum.

Dla FlexGrafik (mały automated print/Wizard) pierwsze NBA **deterministyczne**, nie ML:

1. High-value Wizard abandoned / stuck → follow-up SLA  
2. Wizard completed, brak next step → human push (nie auto-rabat)  
3. Spec/cena poza guardrailem marży → L2 review  
4. Krok wymaga Order Desk którego nie ma → **PARKED handoff**, nie CRITICAL fire  
5. Analytics stale → karta **data quality**, nie sales CRITICAL  

---

## 3. Mapowanie na VHQ (as-is → research gap)

| ID | As-is | Branżowy kontrakt | Lever |
|----|-------|-------------------|-------|
| E1 | CEO stub × N CRITICAL | Stub ∉ Decide-now; TTL; group lub hygiene | **Data/policy** first |
| E2 | Freshness/GA4 always red | Stale = confidence badge; page tylko gdy blocks decision past SLA | **Severity model** |
| E3 | Vault pending=L3 STOP | OK honesty; L1 glance: „0 L2 stamps · 1 L3 STOP” | **Copy / affordance** |
| E4 | Order PARKED | MVP loop = Sales→Wizard only; nie udawać Q2C cash | **Scope honesty** |
| — | Wiele równorzędnych CTA | Jeden primary NBA | **UX rank** |
| — | Q1 money weak | Insufficient_data OK; nie fake KPI; money z Wizard intent gdy jest | **Event contract** |

**Trust (5/5) zostaje.** Naprawiamy **ranking i kontrakt sygnału**, nie „uspokajanie UI”.

---

## 4. Co rusza przychód vs co tylko redukuje lęk

### Revenue movers (priorytet planu)

1. Usunięcie stubów z Decide-now → czas Foundera wraca do realnych lead/quote  
2. SLA + outcome na Wizard completed / abandoned high-value  
3. Guardrail marży/spec przed obietnicą  
4. Jedna akcja + owner + zamknięcie karty  
5. (Później) Order SoT → quote-to-paid — tylko po EV-W2-010 unpark z evidence  

### Anxiety cosmetics (niski ROI / unikaj w planie P2)

- 3D, nowe pokoje, więcej pinów  
- Kolory bez zmiany kontraktu CRITICAL  
- AI summary tych samych złych danych  
- Fałszywe zielone KPI  
- Tłumienie czerwieni bez klasyfikacji źródła  

---

## 5. Scoring kart (propozycja badawcza do planu)

**Eligibility gate (przed score):**

```
IF stub OR no_owner OR no_action OR no_timestamp → Hygiene / Context (never Decide-now CRITICAL)
IF L3/L4 safety STOP → Decide-now even if partial data (label unknowns)
ELSE → score
```

**Score (deterministyczny v1):**

```
priority = money_value × p_close × urgency
         + risk_cost
         − uncertainty_penalty(freshness, confidence)
```

Pojemność: Founder Decide-now **≤3**; reszta queue by owner.

---

## 6. MVP commercial loop przy Order PARKED

Uczciwy zakres pomiaru:

`lead/intent → wizard_started → wizard_completed → follow_up → qualified | lost | unknown`

**Nie raportować** jako revenue intelligence: paid conversion, realized margin, production SLA, cash collected — dopóki brak desk SoT.

DoD research→plan Wave „loop lite”: event IDs, stany, owner, SLA, outcome taxonomy, weekly rates (completion, follow-up SLA, response, unknown%).

---

## 7. Metryki sukcesu remedacji (before/after)

| KPI | Cel |
|-----|-----|
| Stub contamination w Decide-now CRITICAL | **0%** |
| Noise ratio (non-actionable / CRITICAL surface) | **&lt;10%** |
| Top-rail actionability (owner+action+deadline+evidence) | **≥95%** |
| Decide-now count cold-open | **1–3** (poza major incident) |
| ≤30s: Founder wskazuje Q3+Q6 poprawnie | **≥90%** dogfood |
| Chronic freshness as primary red | **0** gdy non-blocking |
| Trust calibration (UI ↔ SoT) | **≥95%** (nie pogarszać) |

Baseline: UX-AUDIT Pass · rail ładuje · SNR zły (E1/E2).

---

## 8. Szkielet 3 fal (dla przyszłego planu — nie GO)

| Wave | Nazwa | DoD (binary, skrót) | STOP |
|------|-------|---------------------|------|
| **W1** | SNR / prawda sygnału | Stuby poza CRITICAL; freshness secondary; ≤3 Decide-now; karty z owner/action/evidence | No 3D · no Order LIVE · no Ads |
| **W2** | Ranked NBA Sales→Wizard | Deterministyczny ranking; SLA+outcome Wizard; jeden primary CTA; weekly review rates | No ML black-box · no Mollie |
| **W3** | Loop completeness | Kontrakt quote→order→prod→pay + unpark EV-W2-010 tylko z evidence | Mollie/Ads tylko osobne GO |

**Kolejność sztywna:** W1 przed W2 przed W3. W3 bez W1 = droższy szum.

---

## 9. Ryzyka złej ścieżki

| Ścieżka | Skutek |
|---------|--------|
| 3D / Campus przed SNR | Estetyka legitymizuje fałszywy pożar |
| Więcej roomów | Więcej miejsc na drift statusu, ten sam zły sygnał |
| AI ranking na stubach | Confidence theater |
| Ukrycie PARKED Order | Utrata trust (jedyna obecna przewaga) |
| „Uspokoić” UI bez kontraktu CRITICAL | Habituacja zostaje, wraca natychmiast |

---

## 10. Rekomendacja sztabu → wejście do planu

**Jedna ścieżka:** przygotować plan gate **`VF-VHQ-P2-SNR-00`** (W1 z §8), oparty o:

1. Kontrakt CRITICAL / eligibility  
2. Lifecycle CEO stub (`STUB` + TTL + out of Decide-now)  
3. Freshness severity model (confidence vs page)  
4. MC L1: Decide-now (≤3) vs Context  
5. Metryki §7 + dogfood ≤30s  

**Następny krok ludzki:** Founder GO na *napisanie planu* P2-SNR-00 (osobno od implementacji).  
Bez GO: research zostaje SoT; idle; 3D/MKT/Order LIVE parked.

---

## 11. Artefakty powiązane

- Expert verify: `docs/handoffs/2026-07-31-VF-VHQ-UX-AUDIT-00-EXPERT-VERIFY.md`  
- UX audit report: `docs/handoffs/2026-07-31-VF-VHQ-UX-AUDIT-00-REPORT.md`  
- Program goal: `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` §1  
- ARCH Q1–Q7: `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md` §3  

RESEARCH_VERDICT: **W1 SNR first · NBA deterministic · no 3D · preserve honesty**
