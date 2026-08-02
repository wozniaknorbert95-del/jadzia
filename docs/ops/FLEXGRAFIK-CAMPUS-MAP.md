---
status: "[ACTIVE]"
title: "FlexGrafik Virtual Campus v1 — operational SoT map"
gate: "VF-CAMPUS-01"
updated: "2026-07-27"
owner: "Norbert Wozniak (Dowódca)"
program_sot: "docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md"
supersedes: "QuietForge_Architektura (input only) · FLEXGRAFIK-VIRTUAL-CAMPUS-BRIEF seed"
evidence:
  vcms_scan: "Conflicts: 0 @ 2026-07-27"
  prod_tip: "4cf66fe"
  commander: "https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08"
  health: "healthy (ssh_connection=ok, worker_loop_alive=true, sqlite=true) · INC-SSH-RECOVERY-00 CLOSED 2026-07-31"
budget_freeze_until: "2026-08-06"
---

# FlexGrafik Virtual Campus v1

**Cel:** operacyjna mapa całej firmy FlexGrafik B.V. — piętra → pomieszczenia → biurka (agenci) → ekrany (dashboardy).  
**Nie jest to gra 3D.** To SoT nawigacji biznesowej **grounded in LIVE** (VCMS + VPS + pitch claims z dowodem).

**Metafora:** Jadzia = COO poruszająca się między pokojami. Dowódca = Mission Control + Boardroom.

```text
                    ┌─────────────────────────────────┐
                    │  P3 GOVERNANCE (Govern brain)    │
                    │  Boardroom · Mission Control     │
                    │  Agent OS · VCMS · Approval Vault │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │  P2 BACK OFFICE (Operate spine) │
                    │  Finance · Knowledge · AI Lab    │
                    │  Compliance · Process Catalog    │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │  P1 COMMERCIAL (Client face)    │
                    │  Reception · Wizard · Game      │
                    │  Sales · Design · Marketing     │
                    │  Brand Portal · Support         │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │  PARTER ORDER / PRODUCTION      │
                    │  Order Desk · Calendar · Proof  │
                    │  Erka HITL · Dispatch PARK      │
                    └────────────────┬────────────────┘
                                     │
                    ┌────────────────┴────────────────┐
                    │  MAGAZYN / DOCK                  │
                    │  Asset Warehouse · Media CDN     │
                    │  Supplier Dock ROADMAP           │
                    └─────────────────────────────────┘
```

**Trzy mózgi (pitch = LIVE):**

| Mózg | Repo / URL | Campus |
|------|------------|--------|
| **Govern** | `flex-vcms` · `cmd.flexgrafik.nl` + `flexgrafik-meta` | P3 Boardroom + VCMS |
| **Build** | `agent-os` · `agent-os-ui` · `os.flexgrafik.nl` | P3 Agent OS Control |
| **Operate** | `jadzia-core` · Commander `?v=mkt-dash08` | P3 Mission Control + P1–Parter ops |

---

## Status legend

| Status | Znaczenie |
|--------|-----------|
| **LIVE** | Prod evidence (URL 200 / E2E / tip / handoff PASS) |
| **PARTIAL** | Kod/docs działają; brak pełnego dashboardu, hop broken, lub park HITL |
| **PARK** | Świadomie wstrzymane (freeze / GO / brak tokenu) |
| **ROADMAP** | Pitch / plan — brak runtime evidence |

---

## D1 — Mapa pomieszczeń (każde z 8 repo ≥1 pokój)

### PIĘTRO 3 — Owner / Governance

| Pomieszczenie | Repo / URL | Status | Agenci | SoT data | Dashboard | KPI | HITL |
|---------------|------------|--------|--------|----------|-----------|-----|------|
| **Boardroom** | `flexgrafik-meta` · `docs/core/master-plan.md` | LIVE (docs) | — | master-plan · global-rules · scorecard mirrors | VCMS docs / repo | Etapy 1–5 alignment | Dowódca strategia |
| **Mission Control** | `jadzia-core` · [Commander](https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08) | **LIVE** | COI · brief · CS · MB rail | `jadzia.db` · tickets · audit | Start + Ops rail | cold open ≤10s · queue clear | Ack/Snooze/Close · GO deploy |
| **Agent OS Control** | `agent-os` + `agent-os-ui` · [os.flexgrafik.nl](https://os.flexgrafik.nl) | **LIVE** | LangGraph runner · HITL approve | OS tasks DB | Mission Control UI | task approve→DONE | Basic Auth · approve/done |
| **VCMS Command** | `Flex-vcms/flex-vcms` · [cmd.flexgrafik.nl](https://cmd.flexgrafik.nl) | **LIVE** | vcms-scan | `data/vcms.db` · conflicts.md | Command Center | **Conflicts: 0** | Basic Auth |
| **Approval Vault** | `jadzia-core` handoffs · Commander Audyt | **LIVE** | audit hash-chain | `docs/handoffs/` · audit API | Audyt (secondary) | chain verify | Zasada 11 GO |

### PIĘTRO 2 — Back Office

| Pomieszczenie | Repo / URL | Status | Agenci | SoT data | Dashboard | KPI | HITL |
|---------------|------------|--------|--------|----------|-----------|-----|------|
| **Finance Room** | jadzia DTL · [UNIT-ECONOMICS](./marketing/UNIT-ECONOMICS.md) · Mollie | **PARTIAL** | costs API · DTL clocks | UNIT-ECONOMICS · costs | Analityka (Commander) | CPA_wizard · margin ≥60% | **Purchase PARK** · Mollie LIVE GO |
| **Knowledge Library** | jadzia [KNOWLEDGE-SYSTEM-INDEX](./KNOWLEDGE-SYSTEM-INDEX.md) | **LIVE** | — | SoT hierarchy | docs index | zero conflicting canons | — |
| **Data & AI Lab** | jadzia MB · eval · analytics INT-009 | **LIVE** | MB propose · analytics_node | `brain_events` · GA4 snapshots | MB Decision Rail · Analityka | MB accuracy · propose-only | MB APPROVE = ticket (nie Ads) |
| **Compliance** | jadzia `AGENTS.md` · Gate D parks | LIVE (docs) | — | hard STOP list | parks w OPERATOR-TODAY | zero fake PASS | Gate D / secrets |
| **Process Catalog** | [PROCESS-CATALOG](./PROCESS-CATALOG.md) | **LIVE** | — | 10/10 L1 cards | catalog MD | ≥80% critical covered | — |

### PIĘTRO 1 — Commercial / Client

| Pomieszczenie | Repo / URL | Status | Agenci | SoT data | Dashboard | KPI | HITL |
|---------------|------------|--------|--------|----------|-----------|-----|------|
| **Reception / Concierge** | jadzia widget · Telegram | **LIVE** | customer_agent · TG ops | widget sessions · intents | Home queue · TG | sessions · intent route | TG HITL |
| **Showroom / Wizard** | `zzpackage.flexgrafik.nl` · [/wizard/](https://zzpackage.flexgrafik.nl/wizard/) | **LIVE** | design-agent (in-wizard) · widget | product-master · WC | Wizard funnel | checkout ≥€199 · IC | checkout / offerte |
| **Lead Game** | `app.flexgrafik.nl` | **LIVE** | INT-004 ingest | `leads` table | game + leads API | lead→coupon→Wizard | — |
| **Sales Room** | jadzia REV-DEMAND | **LIVE** | lead_node · sales_cta | leads · hot_lead tickets | Home CRITICAL/ACTION | Lead→Wizard · SLA | disposition Ack |
| **Design Studio** | zzpackage design-agent · jadzia INSPIRE | **PARTIAL** | inspire · design-agent | mockups / briefs | Wizard DA UI · hop health **historically 404** | mockup before price | brief edit HITL |
| **Marketing Studio** | jadzia Demand OS Hub · [OPERATOR-TODAY](./marketing/OPERATOR-TODAY.md) · [TOOL-PASS](./demand-os/TOOL-PASS.md) | **LIVE** (Hub §M tool) / **PARKED_LAST** (HITL publish) / **PARK** (paid) | Hub status · money-check · Val gate | CONTENT-CALENDAR.json · UTM Lock · GROWTH-EVENTS | Commander `demand-os/status` + Marketing tab | wizard_starts UTM · val FAIL · top_hook | **Ads PARK cash** · no live publish without GO |
| **Brand Portal** | `flexgrafik-nl` · flexgrafik.nl | **PARTIAL** | portal_qualify INT-012 | WP content | portal pages | trust → Wizard/Game | deploy GHA |
| **Client Support** | jadzia `cs_followup` · SPEED-TO-LEAD | **PARTIAL** | cs_followup | CS tickets | Home CS form | WA &lt;15 min | Ack follow-up |

### PARTER — Order / Production

| Pomieszczenie | Repo / URL | Status | Agenci | SoT data | Dashboard | KPI | HITL |
|---------------|------------|--------|--------|----------|-----------|-----|------|
| **Order Desk** | jadzia INT-002 WC webhook | **LIVE** | order_node | `orders` · **#3149** proof | orders in DB / Home | order ingest SLA | exception fix |
| **Content / Calendar** | jadzia content_calendar · FB/TT | **LIVE** | content_calendar_node · facebook/tiktok pub | calendar entries · fb_post_id | Marketing kolejka | publish success | approve / undo 60s |
| **Preflight / Proof** | design-agent · M2 video | **PARTIAL** | inspire · media probe | media_url · publish_result | Marketing + DA | preflight pass | approve media |
| **Production Network** | Erka / partner (external) | HITL | — | manual partner status | — | on-time wrap | Dowódca ↔ Erka |
| **Dispatch** | fulfilment tracker | **PARK** | — | — | — | — | roadmap |

### MAGAZYN / Dock

| Pomieszczenie | Repo / surface | Status | Agenci | SoT data | Dashboard | KPI | HITL |
|---------------|----------------|--------|--------|----------|-----------|-----|------|
| **Asset Warehouse** | GDrive `MKT/YYYY-WW/` · [ASSET-MATERIALS-PREP](./marketing/ASSET-MATERIALS-PREP.md) | HITL | — | master_reel · tt_hook · NOTES | Drive folder | WW complete | Dowódca inventory |
| **Media CDN** | verified GDrive URLs → FB/TT | **PARTIAL** | gdrive probe | media_url | Marketing | URL probe OK | — |
| **Supplier Dock** | Procurement Brain (pitch Phase C) | **ROADMAP** | — | — | — | RFQ SLA | future gate |

### Repo coverage matrix (8/8)

| Repo | Tip (local @ scan) | Primary room(s) |
|------|--------------------|-----------------|
| `flexgrafik-meta` | `6a2e4b2` | Boardroom |
| `Flex-vcms/flex-vcms` | `969410d` | VCMS Command |
| `jadzia-core` | local `d427a94` · **prod `4cf66fe`** | Mission Control + Operate rooms |
| `zzpackage.flexgrafik.nl` | `8d2d20e` | Wizard · Design Studio |
| `app.flexgrafik.nl` | `9033c52` | Lead Game |
| `flexgrafik-nl` | `4543e77` | Brand Portal |
| `agent-os` | `7051224` | Agent OS Control |
| `agent-os-ui` | `28de58f` | Agent OS Control (UI) |

**VCMS:** Conflicts **0** (2026-07-27). Prod health: `degraded` SSH (pre-existing; worker + SQLite OK).

---

## D2 — Room cards (pilot ×5)

### Mission Control
- **Piętro:** P3 Governance
- **Repo / URL:** `jadzia-core` · https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08
- **Status:** LIVE
- **Owner (human/agent):** Dowódca / Jadzia COI
- **Agenci / automaty:** brief_node · cs_followup · ticket queue · Ops health strip
- **Dane (SoT):** `jadzia.db` tickets · worker health · audit chain
- **Dashboard / wejście:** Commander **Start** (D0.15)
- **KPI (1–3):** cold open ≤10s · CRITICAL+ACTION clear · health ≠ down
- **HITL gate:** Ack/Snooze/Close · deploy GO (Zasada 11)
- **Next action:** Utrzymać hub; campus labels w System Map (bez 6th tab)

### Showroom / Wizard
- **Piętro:** P1 Commercial
- **Repo / URL:** `zzpackage.flexgrafik.nl` · https://zzpackage.flexgrafik.nl/wizard/
- **Status:** LIVE
- **Owner (human/agent):** Cash Engine / design-agent + widget
- **Agenci / automaty:** product configurator · widget INT-001 · offerte concierge
- **Dane (SoT):** `system/data/product-master-table.json` · WC · Mollie checkout path
- **Dashboard / wejście:** Wizard SPA · Commander hop
- **KPI (1–3):** min checkout €199 · marża ≥60% · InitiateCheckout
- **HITL gate:** real Purchase / Mollie LIVE = PARK (osobne GO)
- **Next action:** organic UTM → wizard_starts (po WW assets)

### Marketing Studio
- **Piętro:** P1 Commercial
- **Repo / URL:** `jadzia-core` Demand OS Hub · `docs/ops/demand-os/` · Commander Marketing
- **Status:** LIVE (Hub §M tool) · PARKED_LAST (HITL publish) · PARK (Ads cash)
- **Owner (human/agent):** Growth Lead / Dowódca
- **Agenci / automaty:** Demand OS F1–F4 + Hub · Val gate · A2A (publish HITL parked)
- **Dane (SoT):** OS TARGET · CONTENT-CALENDAR.json · UTM Lock · GROWTH-EVENTS · MEMORY.json
- **Dashboard / wejście:** Commander `GET /api/v1/commander/demand-os/status` + Marketing tab
- **KPI (1–3):** wizard_starts UTM · validator_fail · top_hook (no vanity views)
- **HITL gate:** live publish only after `GO MARKETING HITL` · **€0 Ads**
- **Next action:** dashboard tip complete · marketing remains PARKED_LAST

### Order Desk
- **Piętro:** Parter Order/Production
- **Repo / URL:** `jadzia-core` INT-002 · WC webhook
- **Status:** LIVE
- **Owner (human/agent):** order_node / Dowódca exceptions
- **Agenci / automaty:** `POST /webhooks/woocommerce/order` · order_node
- **Dane (SoT):** `orders` table · proof **order #3149** (INT-002 E2E)
- **Dashboard / wejście:** SQLite / ops (brak osobnego UI tab — widać przez spine + Home)
- **KPI (1–3):** webhook OK · order→calendar suggest · exception rate
- **HITL gate:** data fix · Gate D parked
- **Next action:** Keep spine; Dispatch nadal PARK

### Finance Room
- **Piętro:** P2 Back Office
- **Repo / URL:** UNIT-ECONOMICS · costs API · Mollie (zzpackage)
- **Status:** PARTIAL
- **Owner (human/agent):** Dowódca / costs + DTL
- **Agenci / automaty:** costs routes · DTL SLA clocks · (brak full finance agent)
- **Dane (SoT):** UNIT-ECONOMICS.md · spend/CPL/CPA definitions
- **Dashboard / wejście:** Commander **Analityka** (częściowo) · docs
- **KPI (1–3):** CPA_wizard &lt; 0.40×marża · margin ≥60% · purchases&gt;0
- **HITL gate:** H-Purchase Mollie · paid spend unlock 2026-08-06
- **Next action:** Po organic WW — instrumentacja; Purchase tylko z GO

---

## D3 — Gap analysis: pitch deck vs reality (top 5)

Źródło claims: `Pitch-Deck-2026.pdf` (14 pp). Reality: VPS tip `4cf66fe`, scorecard #1–9 LIVE, handoffs INT/Commander.

| # | Pitch claim | Reality | Gap | Next action |
|---|-------------|---------|-----|-------------|
| 1 | **Procurement Brain / RFQ** (Phase C, 12 mo) | Brak runtime; Supplier Dock = ROADMAP | Product wedge SaaS nie istnieje | Osobny gate po Print Pack pilots — **nie** w tej sesji |
| 2 | **Print Pack tenants / SaaS €100+2%** | Pre-revenue platform (pitch honest); service cash only | Zero paying Print Pack tenants | GTM organic → 3 pilots (roadmap 90d) — po assets |
| 3 | **Production / Fulfillment agent** | Erka = HITL manual; Dispatch PARK | Brak fulfilment dashboard | Keep HITL; nie fake LIVE |
| 4 | **Finance agent** (PARTIAL w deck) | UNIT-ECONOMICS docs + costs; **Purchase PARK**; brak finance agent | Dashboard finansowy niepełny | Analityka + UE; Mollie GO osobno |
| 5 | **Design PARTIAL** + hop `design-agent/health` | Design UI w Wizard LIVE; public health hop **404** (audit 2026-07-21) | System Map trust broken dla DA | Fix health route **lub** hop → real Wizard DA URL (CMD-DASH residual) |

**Claims z dowodem (nie luki):** Order **#3149** · INT-001–010 spine · COI Commander LIVE · Agent OS HITL · VCMS Conflicts 0 · Sales/Governance LIVE · Marketing content LIVE · paid campaigns gated (dziś freeze).

**Odrzucone z QuietForge draft:** 3D décor, Client Portal multi-role RBAC theatre, Supplier Gate UI bez RFQ backend, „półki produktowe” bez product-master link — u nas Showroom = **Wizard**, nie mock sklep.

---

## D4 — Commander IA proposal (campus → UI, bez fake tab)

**Decyzja:** Campus = **SoT dokument + etykiety hopów**, nie 6. primary tab. Szanuje **D0.15** (5 primary) i **D0.19** (deep-link, no merge).

| Campus room | Existing Commander surface | Change? |
|-------------|---------------------------|---------|
| Mission Control | **Start** (Home) + Ops strip | Label only: „Mission Control” w home-sub |
| Marketing Studio | **Marketing** + MB rail | Already = room |
| Finance / Data Lab | **Analityka** | PARTIAL — KPI z UNIT-ECONOMICS w hint |
| Agenci desks | **Agenci** | Map agent → room name in cards |
| Approval Vault | **Audyt** (secondary via Ustawienia) | Keep secondary |
| Boardroom / VCMS / Agent OS / Wizard / DA | **Mapa systemu** (Home + Ustawienia) | Add campus floor tags in hop-meta copy (docs-first; code optional later) |
| Order Desk | Home queue / spine (no dedicated tab) | **Nie** dodawać taba — link w Agenci/Order card |
| Asset Warehouse | Marketing → Drive folder hint | Already |

**Zakaz:** nowy tab „Campus” / „Firma” / 6th Audyt peer.

**Opcjonalny follow-up (osobny gate UI):** `hop-meta` text = `P3 · VCMS` / `P1 · Wizard` — zero nowych views.

---

## D5 — Plan `MKT/2026-W31/` (Marketing + Design Studio)

ISO week od 2026-07-27 = **W31**. Parent: [ASSET-MATERIALS-PREP](./marketing/ASSET-MATERIALS-PREP.md).

| Krok | Owner | Done when |
|------|-------|-----------|
| 1. Inventory (Outcome A) | Dowódca + agent | Lista: bus foto/wideo · stare FB/TT · INSPIRE mockupy · braki |
| 2. Repo scout (Outcome B) | agent | 1–3 szablony · ADAPT/FORK/SKIP |
| 3. WW v0 folder | Dowódca HITL | `MKT/2026-W31/` z min. `master_reel_9x16` **lub** shoot plan + placeholders + `NOTES.md` |
| 4. Design Studio link | zzpackage DA | 1 mockup wrap → still do carousel (P1 po freeze OK) |
| 5. Publish path | Commander | FB organic po WW; TT po `TIKTOK_ACCESS_TOKEN` |

**NOTES.md seed:**

```markdown
# MKT/2026-W31
hypothesis: ZZP bouw herkenbaarheid bus — gratis check → Wizard
utm_campaign: zzp_branding_check_v1
channels: meta organic, tiktok organic
cta: wizard utm_source=tiktok|meta medium=organic
asset_source: [own shoot | repo NAME | reuse FILE]
dowodca_approval: [ ] publish FB  [ ] publish TT
campus_room: Marketing Studio · Design Studio
```

**STOP:** Ads spend · Mollie · deploy bez GO · IG.

---

## Evidence log (VF-CAMPUS-01)

| Check | Result |
|-------|--------|
| `node tools/vcms-scan.js` | Conflicts: **0** |
| `GET …/worker/health` | `degraded` · worker alive · sqlite true · ssh error |
| `GET …/commander/?v=mkt-dash08` | HTTP **200** |
| Pitch extract | 14 pages · LIVE vs ROADMAP agents table used |
| QuietForge arch | floors kept · décor rejected |
| Scorecard AI OS | #1–9 **LIVE** |

---

## Next gate

**Program SoT:** [FLEXGRAFIK-CAMPUS-PROGRAM.md](./FLEXGRAFIK-CAMPUS-PROGRAM.md) (VF-CAMPUS-PLAN-00 CLOSE).  
**Active:** `MKT-ASSET-00` → `MKT/2026-W31/` (Asset+Experiment Cards).  
**Unblocked:** `VF-CAMPUS-W1` (tylko po C1 Founder — nie w tej samej sesji co MKT).  
Campus map v1 = atlas; program = fale + Evidence Ledger.

)
