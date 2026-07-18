# Scorecard — FlexGrafik AI Operating System (zaliczenie)

**Status:** ACTIVE — TRUTH REPAIR 2026-07-18  
**Program:** AI OS + AI MBA (plan v2)  
**Owner:** Dowódca (GO / dogfood) / Agent (pomiar + artefakty)  
**SoT tip:** VPS `/opt/jadzia` `git rev-parse --short HEAD`  
**Uwaga:** statusy poniżej są **surowe** — nie mylić „docs shipped” z „zaliczeniem programu”.

## Warunki zaliczenia (9)

| # | Warunek | Definicja operacyjna | SoT / powierzchnia | Status | Dowód | Następny gate |
|---|---------|----------------------|--------------------|--------|-------|---------------|
| 1 | Dashboard CEO | Cold open ≤10s; daily &lt;5 min; kolejka + mapa | `/commander/` | **LIVE** | Agent dogfood PASS @ tip `2ba7c85` (`UX-DOGFOOD-PHONE.md`) | maintain; residual TG live optional |
| 2 | System wiedzy | Indeks SoT + procesy; zero sprzecznych kanonów | KNOW-00 + catalog | **PARTIAL** | Index w jadzia only; **meta/VCMS bez linku** | Mirror meta lub VCMS docs |
| 3 | AI Sprzedawca | Lead→CTA→Wizard | Demand + widget | LIVE | REV-DEMAND F0–F7 | maintain |
| 4 | AI Marketing | Draft→HITL→publish | Commander Marketing | LIVE | PUBLISH-B + audit publish×8/14d | maintain |
| 5 | AI Project Manager | Orkiestracja HITL | Agent OS | **PARTIAL** | Deep-link only (nie agent w jadzia) | rytuał OS / kontrakt |
| 6 | AI Customer Success | Post-sale follow-up | `cs_followup` | **PARTIAL** | Spawn+queue; **brak API/UI** | CS API+UI (osobna sesja) |
| 7 | AI Asystent Zarządu | Brief→HITL→Home | brief_node | LIVE | STRATEGY-HITL + tickets | maintain |
| 8 | ≥80% procesów opisanych | karty L1 critical | PROCESS-CATALOG | **PARTIAL** | 10 kart MD (**papier**; nie VCMS-linked) | PROC hygiene / VCMS mirror |
| 9 | ≥60% ops AI | 14d ratio | OPS-AI-SCORECARD | **FAIL / in_progress** | **Measured 45.8%** (v1) | podnieś AI ops lub re-window |

## Mapa 5 ról AI → powierzchnie

| Rola | Powierzchnia | Status |
|------|--------------|--------|
| AI Sprzedawca | widget + sales_cta | LIVE |
| AI Marketing | marketing agent + publish | LIVE |
| AI Project Manager | hop `os.flexgrafik.nl` | PARTIAL (link) |
| AI Customer Success | `cs_followup` stub | PARTIAL |
| AI Asystent Zarządu | brief HITL | LIVE |

## Baseline (zmierzony)

| Miernik | Wartość | Data |
|---------|---------|------|
| % procesów critical z kartą MD | 10/10 opisane (docs-only) | 2026-07-18 |
| % ops AI (14d, v1 contract) | **45.8%** (11 AI / 13 human) | 2026-07-18 VPS |

## RACI

| Rola | Odpowiedzialność |
|------|------------------|
| Dowódca | GO deploy, **phone dogfood**, akceptacja MBA Week N |
| Agent | Artefakty, kod, pomiar, handoff — **bez fałszywego PASS** |
| Delegat | Eskalacje SLA (D0.9) |

## STOP

Gate D / Mollie LIVE / min199 / merge OS-VCMS / sekrety / deploy bez GO / oznaczanie INTERIM jako completed.
