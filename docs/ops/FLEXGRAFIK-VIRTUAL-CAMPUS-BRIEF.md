---
status: "[SUPERSEDED]"
title: "FlexGrafik Virtual Campus — research & SoT brief"
gate: "VF-CAMPUS-01"
updated: "2026-07-27"
owner: "Norbert Wozniak (Dowódca)"
superseded_by: "docs/ops/FLEXGRAFIK-CAMPUS-MAP.md"
supersedes: "QuietForge_Architektura (external draft — input only)"
inputs:
  - "Pitch-Deck-2026.pdf (QuietForge / FlexGrafik B.V.)"
  - "QuietForge_Architektura_Wirtualnej_Firmy.md (input — we build better, grounded in LIVE)"
  - "flex-vcms/docs/ecosystem/map.md"
  - "docs/ops/marketing/GTM-1PAGER.md"
budget_freeze_until: "2026-08-06"
---

# FlexGrafik Virtual Campus — brief badawczy

> **SoT v1 map:** [FLEXGRAFIK-CAMPUS-MAP.md](./FLEXGRAFIK-CAMPUS-MAP.md)  
> **Program SoT (PLAN-00):** [FLEXGRAFIK-CAMPUS-PROGRAM.md](./FLEXGRAFIK-CAMPUS-PROGRAM.md) — ten brief = seed research only.

## Cel (nie gra — operacyjna siedziba)

**Cyfrowa siedziba FlexGrafik B.V.:** każde pomieszczenie = prawdziwy dział, repo, dane, kolejka, dashboard.  
Dowódca widzi **cały biznes** z jednego modelu — nie tylko Marketing.

**Lepsze niż QuietForge draft:** mapa musi być **grounded in LIVE** (pitch deck + VPS evidence), nie wishful 3D.

---

## Trzy mózgi (pitch deck SoT)

| Mózg | Repo / URL | Rola w campusie |
|------|------------|-----------------|
| **Govern** | `flex-vcms` · `flexgrafik-meta` | Piętro 3 — polityki, konflikty, workflow |
| **Build** | `agent-os` · `agent-os-ui` | AI Lab + Mission Control (build HITL) |
| **Operate** | `jadzia-core` · Commander | COI — Sense→Think→Propose→Act→Guard |

---

## Ekosystem repo → pomieszczenia (seed map — do weryfikacji research)

### PIĘTRO 3 — Owner / Governance

| Pomieszczenie | Repo / surface | LIVE? | Co widać (dashboard) |
|---------------|----------------|-------|----------------------|
| Boardroom | `flexgrafik-meta` master-plan | docs | strategia, zasady, scorecard |
| Mission Control | Commander `?v=mkt-dash08` | **LIVE** | Ops rail · MB rail · agents · KPI |
| Agent OS Control | `os.flexgrafik.nl` :8080 | **LIVE** | task HITL · approve/done |
| VCMS Command | `cmd.flexgrafik.nl` | **LIVE** | scan · conflicts · ecosystem map |
| Approval Vault | Commander audit · handoffs | **LIVE** | decyzje · GO · audit trail |

### PIĘTRO 2 — Back Office

| Pomieszczenie | Repo / moduł | LIVE? | Dashboard |
|---------------|--------------|-------|-----------|
| Finance Room | DTL · UNIT-ECONOMICS · Mollie | PARTIAL | margin · CPA · Purchase PARK |
| Knowledge Library | `docs/ops/KNOWLEDGE-SYSTEM-INDEX` | **LIVE** | SoT hierarchy |
| Data & AI Lab | MB shadow · eval · Chroma | **LIVE** | accuracy · propose preflight |
| Compliance | AGENTS.md · Gate D · privacy | docs | parks · hard STOP |
| Process Catalog | `PROCESS-CATALOG.md` | **LIVE** | L1 processes |

### PIĘTRO 1 — Commercial / Client

| Pomieszczenie | Repo / URL | LIVE? | Dashboard |
|---------------|------------|-------|-----------|
| Reception / Concierge | Widget chat · Telegram | **LIVE** | sessions · intents |
| Showroom / Wizard | `zzpackage` Wizard | **LIVE** | funnel · checkout IC |
| Lead Game | `app.flexgrafik.nl` | **LIVE** | INT-004 leads |
| Sales Room | REV-DEMAND · lead queue | **LIVE** | hot_lead · disposition |
| Design Studio | INSPIRE · design-agent | **LIVE** | generate · mockup |
| Marketing Studio | Marketing OS · GTM | **LIVE** | organic · freeze · TT |
| Brand Portal | `flexgrafik-nl` | partial | content · SEO |
| Client Support | CS followup · SPEED-TO-LEAD | PARTIAL | SLA · tickets |

### PARTER — Order / Production

| Pomieszczenie | Repo / integracja | LIVE? | Dashboard |
|---------------|-------------------|-------|-----------|
| Order Desk | INT-002 WC webhook · orders | **LIVE** | order #3149 proof |
| Content / Calendar | content_calendar · FB/TT publish | **LIVE** | calendar · publish status |
| Preflight / Proof | design-agent · M2 video | PARTIAL | fb_post_id · gates |
| Production Network | Erka / partner (external) | HITL | manual status |
| Dispatch | fulfilment (roadmap) | PARK | — |

### MAGAZYN / Dock

| Pomieszczenie | Co | LIVE? |
|---------------|-----|-------|
| Asset Warehouse | GDrive `MKT/YYYY-WW/` | HITL |
| Media CDN | verified URLs FB/TT | PARTIAL |
| Supplier Dock | Procurement Brain | ROADMAP (pitch Phase C) |

---

## Deliverable sesji badawczej (VF-CAMPUS-01)

Jedna sesja = **research + v1 SoT document**. Nie implementacja 3D.

| # | Output | Acceptance |
|---|--------|------------|
| D1 | **`FLEXGRAFIK-CAMPUS-MAP.md`** | Każde repo w ≥1 pomieszczeniu · status LIVE/PARTIAL/PARK/ROADMAP · URL/dashboard |
| D2 | **Room card template** (×5 min pilot) | Pomieszczenie: owner · agenci · dane · KPI · HITL gate · linki |
| D3 | **Gap analysis** | Pitch deck obietnice vs reality · top 5 luk |
| D4 | **MKT/YYYY-WW/** plan | Pod Marketing Studio + Design — [ASSET-MATERIALS-PREP](./marketing/ASSET-MATERIALS-PREP.md) |
| D5 | **Commander IA proposal** | Jak campus mapuje się na istniejący UI (nie fake tab) |

---

## Metodologia research (obowiązkowa)

1. **VCMS scan** — `node tools/vcms-scan.js` · conflicts=0
2. **Per repo** (8): brain · todo · last handoff · prod tip jeśli dotyczy
3. **Pitch deck** — extract LIVE vs ROADMAP claims (już częściowo w deck)
4. **QuietForge doc** — import struktury pięter · **odrzuć** dekoracje bez danych
5. **Evidence** — VPS tip `4cf66fe` · Commander · INT proofs · nie zgaduj

---

## Constraints (Dowódca)

| Constraint | Value |
|------------|-------|
| Budget freeze | **€0 paid Meta** do **2026-08-06** |
| Deploy | Zasada 11 — GO only |
| QuietForge product | `services/` — **zero** w jadzia-core runtime |
| IG | out of scope |
| Fake PASS | zakaz |

---

## Room card — szablon

```markdown
## [Nazwa pomieszczenia]
- **Piętro:** …
- **Repo / URL:** …
- **Status:** LIVE | PARTIAL | PARK | ROADMAP
- **Owner (human/agent):** …
- **Agenci / automaty:** …
- **Dane (SoT):** …
- **Dashboard / wejście:** …
- **KPI (1–3):** …
- **HITL gate:** …
- **Next action:** …
```

---

## Kolejność po campus v1

1. Asset materials (Marketing + Design Studio)
2. FB/TT organic publish (freeze)
3. Meta paid po 2026-08-06
4. Procurement Brain (pitch Phase C) — osobny gate
