# Scorecard — FlexGrafik AI Operating System (zaliczenie)

**Status:** ACTIVE (baseline 2026-07-18)  
**Program:** AI OS + AI MBA (plan v2)  
**Owner:** Dowódca (GO) / Agent (pomiar + artefakty)  
**SoT tip:** aktualizuj przy każdym gate CLOSE

## Warunki zaliczenia (9)

| # | Warunek | Definicja operacyjna | SoT / powierzchnia | Status | Dowód | Następny gate |
|---|---------|----------------------|--------------------|--------|-------|---------------|
| 1 | Dashboard CEO | Cold open ≤10s „wiem co dziś”; daily &lt;5 min; 3 priorytety + kolejka + mapa | `/commander/` | LIVE | UX-00..03 + MOBILE/MAP | dogfood phone |
| 2 | System wiedzy | Indeks SoT + procesy z kartami; zero sprzecznych kanonów | KNOW-00 + PROCESS-CATALOG | LIVE | KNOW-00 + PROC-01 | maintain |
| 3 | AI Sprzedawca | Lead→CTA→disposition→Wizard (min 199, wizard-only) | Demand + widget | LIVE | REV-DEMAND F0–F7; `sales_cta` | dogfood / maintain |
| 4 | AI Marketing | Draft→HITL approve→publish/undo | Commander Marketing | LIVE | COI-MARKETING-PUBLISH-B | polish park |
| 5 | AI Project Manager | Hop Agent OS + HITL diffs (bez merge) | `https://os.flexgrafik.nl` | LIVE | MAP-01 deep-link + Agents tab | rytuał Dowódca |
| 6 | AI Customer Success | Post-sale / retention / support tor | `cs_followup` queue | PARTIAL | CS-01 spawn+queue; auto-trigger later | Week 18–19 MBA |
| 7 | AI Asystent Zarządu | Brief→HITL tickets→Home | `brief_node` + Home | LIVE | COI-STRATEGY-HITL-01 + sales CTA | UX czytelność |
| 8 | ≥80% procesów opisanych | `covered_critical / critical_L1 ≥ 0.80` | `PROCESS-CATALOG.md` | LIVE | 10/10 cards | maintain |
| 9 | ≥60% ops AI | 14d ratio; CRITICAL HITL excluded | `OPS-AI-SCORECARD.md` | INTERIM | window → 2026-08-01 | fill numbers |

## Mapa 5 ról AI → powierzchnie

| Rola | Powierzchnia | `agent_id` / hop | Status |
|------|--------------|------------------|--------|
| AI Sprzedawca | Widget chat + leads + `sales_cta` queue | customer path / leads (nie zawsze w `/agents`) | LIVE |
| AI Marketing | Marketing tab + publish HITL | `marketing` | LIVE |
| AI Project Manager | Agent OS Mission Control | `engineering` → `https://os.flexgrafik.nl` | LIVE |
| AI Customer Success | (cs_followup queue) | PARTIAL → auto later | PARTIAL |
| AI Asystent Zarządu | Brief + Home priorities / ops HITL | brief_hitl + Home | LIVE |

**Uwaga:** Design/INSPIRE (`design`) i inne Phase C placeholdery nie zastępują 5 ról zaliczeniowych — mapowanie w `COI-ROLE-01`.

## Baseline TBD

| Miernik | Baseline | Data |
|---------|----------|------|
| % procesów krytycznych z kartą | TBD (`COI-PROC-00`) | — |
| % ops AI (14d) | TBD (`COI-OPS-AI-00`) | — |

## RACI

| Rola | Odpowiedzialność |
|------|------------------|
| Dowódca | GO deploy, phone dogfood, akceptacja MBA Week N |
| Agent | Artefakty, kod, pomiar, handoff |
| Delegat | Eskalacje SLA (D0.9) |

## STOP (skrót)

Gate D / Mollie LIVE / min199 / merge OS-VCMS / sekrety w lekcjach / deploy bez GO.
