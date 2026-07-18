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
| 2 | System wiedzy | Indeks SoT + procesy; zero sprzecznych kanonów | KNOW-01 mirrors | **LIVE** | SoT jadzia + meta/VCMS pointers (COI-KNOW-01) | maintain; #8 proces VCMS-link osobno |
| 3 | AI Sprzedawca | Lead→CTA→Wizard | Demand + widget | LIVE | REV-DEMAND F0–F7 | maintain |
| 4 | AI Marketing | Draft→HITL→publish | Commander Marketing | LIVE | PUBLISH-B + audit publish×8/14d | maintain |
| 5 | AI Project Manager | Orkiestracja HITL | Agent OS | **PARTIAL** | Deep-link only (nie agent w jadzia) | rytuał OS / kontrakt |
| 6 | AI Customer Success | Post-sale follow-up | `cs_followup` | **LIVE** | API+UI HITL tip `0a54bc7`; dogfood spawn→Ack | maintain; auto-trigger later |
| 7 | AI Asystent Zarządu | Brief→HITL→Home | brief_node | LIVE | STRATEGY-HITL + tickets | maintain |
| 8 | ≥80% procesów opisanych | karty L1 critical | PROCESS-CATALOG | **PARTIAL** | 10 kart MD (**papier**; nie VCMS-linked) | PROC hygiene / VCMS mirror |
| 9 | ≥60% ops AI | 14d ratio | OPS-AI-SCORECARD | **LIVE / PASS** | **60.6%** v1.1 (20/33) tip `d97939a` | maintain; re-window if human publish spikes |

## Mapa 5 ról AI → powierzchnie

| Rola | Powierzchnia | Status |
|------|--------------|--------|
| AI Sprzedawca | widget + sales_cta | LIVE |
| AI Marketing | marketing agent + publish | LIVE |
| AI Project Manager | hop `os.flexgrafik.nl` | PARTIAL (link) |
| AI Customer Success | Home form + queue HITL | LIVE |
| AI Asystent Zarządu | brief HITL | LIVE |

## Baseline (zmierzony)

| Miernik | Wartość | Data |
|---------|---------|------|
| % procesów critical z kartą MD | 10/10 opisane (docs-only) | 2026-07-18 |
| % ops AI (14d, v1 contract) | **45.8%** (11/24) — historical baseline | 2026-07-18 |
| % ops AI (14d, v1.1) | **60.6%** (20/33) tip `d97939a` — **PASS** | 2026-07-18 post-deploy SQL |

## RACI

| Rola | Odpowiedzialność |
|------|------------------|
| Dowódca | GO deploy, **phone dogfood**, akceptacja MBA Week N |
| Agent | Artefakty, kod, pomiar, handoff — **bez fałszywego PASS** |
| Delegat | Eskalacje SLA (D0.9) |

## STOP

Gate D / Mollie LIVE / min199 / merge OS-VCMS / sekrety / deploy bez GO / oznaczanie INTERIM jako completed.
