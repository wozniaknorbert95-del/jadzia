# Process Catalog L1 — FlexGrafik (COI-PROC-00/01)

**Status:** PARTIAL — karty MD kompletne; **nie** zalicza systemu wiedzy ekosystemu (brak VCMS/meta mirror)  
**Date:** 2026-07-18 (truth repair)  
**Formula:** `covered_critical / critical_L1` (opisane w MD ≠ operacyjne w VCMS)  
**Mianownik critical_L1:** 10 (poniżej, `critical=Y`)

## Baseline (PROC-00)

| Metric | Value |
|--------|-------|
| critical_L1 | 10 |
| covered (full card) at baseline draft | 3 |
| baseline % | 30% |
| after PROC-01 cards | 8 / 10 = **80%** |

## Karty procesów

### P-SALES-01 — Demand lead → Wizard (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | Dowódca / AI Sprzedawca |
| Trigger | Widget chat intent oferta |
| AI | customer_agent reply + CTA + lead create |
| Human | disposition Ack/Snooze/Close; optional |
| HITL | sales_cta queue ACTION |
| SoT | REV-DEMAND handoffs; widget routes |
| Status | LIVE |

### P-SALES-02 — Brief sales CTA spawn (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | AI Asystent Zarządu → Sales |
| Trigger | Weekly brief / spawn_brief_sales_cta |
| AI | spawn tickets score≥40 |
| Human | Ack in Commander |
| HITL | yes |
| SoT | REV-DEMAND-04 CLOSE |
| Status | LIVE |

### P-MKT-01 — Marketing publish HITL (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | AI Marketing |
| Trigger | draft/schedule in Commander |
| AI | calendar + FB publish path |
| Human | approve / undo 60s |
| HITL | yes |
| SoT | COI-MARKETING-PUBLISH-B |
| Status | LIVE |

### P-BOARD-01 — Weekly brief HITL (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | AI Asystent Zarządu |
| Trigger | brief ritual |
| AI | metrics + spawn ops tickets |
| Human | approve/act in Home |
| HITL | yes |
| SoT | COI-STRATEGY-HITL-01 |
| Status | LIVE |

### P-ENG-01 — Agent OS engineering HITL (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | AI Project Manager |
| Trigger | Dowódca hop z mapy / Agents |
| AI | Agent OS orchestration |
| Human | approve diffs in OS |
| HITL | yes (in Agent OS) |
| SoT | D0.6; os.flexgrafik.nl |
| Status | LIVE |

### P-GOV-01 — VCMS governance scan (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | Dowódca |
| Trigger | session start / weekly |
| AI | scan scripts (VCMS) |
| Human | resolve conflicts |
| HITL | human decision |
| SoT | cmd.flexgrafik.nl; Flex-vcms |
| Status | LIVE |

### P-REV-01 — Revenue event INT-002 (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | Revenue / Jadzia consumer |
| Trigger | Mollie/order events (TEST) |
| AI | ingest + reconcile hooks |
| Human | Gate D parked; recon ritual |
| HITL | Gate D |
| SoT | REVENUE-EVENT-CONTRACT; REVENUE-RECONCILIATION |
| Status | PARTIAL (Gate C PASS, D parked) |

### P-CEO-01 — Commander daily loop (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | Dowódca |
| Trigger | TG /commander |
| AI | priorities + queue build |
| Human | act &lt;5 min |
| HITL | CRITICAL |
| SoT | UX-BRIEF; MOBILE-02; UX-01..03 |
| Status | LIVE (UX hardening 2026-07-18) |

### P-CS-01 — Customer Success post-sale (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | Dowódca / AI CS |
| Trigger | manual spawn (Home) — auto paid-order later |
| AI | `POST /api/v1/commander/cs/followup` → ticket `cs_followup` |
| Human | Potwierdź / Odłóż / Zamknij (&lt;48h SLA) |
| HITL | yes |
| SoT | COI-CS-02 CLOSE |
| Status | **LIVE** (manual); auto-trigger out of scope |

### P-EMERGENCY-01 — No-laptop ticket (critical=Y) — COVERED

| Field | Value |
|-------|-------|
| Owner | Dowódca / Delegat |
| Trigger | TG /ticket deep-link |
| AI | signed link + Commander panel |
| Human | resolve |
| HITL | emergency |
| SoT | D0.14; MOBILE |
| Status | LIVE |

## Non-critical (nie w mianowniku 80%)

| id | name | status |
|----|------|--------|
| P-DESIGN-01 | INSPIRE / Design Agent | LIVE hop |
| P-FIN-02 | SMTP Delegat escalation | LIVE ops |
| P-MBA-01 | AI MBA Week N | spine ACTIVE |

## Score

`described_critical = 10/10 = 100%` ≥ 80% → **PASS** (karta istnieje; execution LIVE osobno).  
Execution gaps: CS auto-trigger (PARTIAL), Gate D (parked).
