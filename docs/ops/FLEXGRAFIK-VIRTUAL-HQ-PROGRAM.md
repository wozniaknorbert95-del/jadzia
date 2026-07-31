---
status: "[ACTIVE]"
title: "FlexGrafik Virtual HQ — Program SoT (VF-VHQ-PLAN-00)"
gate: "VF-VHQ-PLAN-00"
updated: "2026-07-31"
owner: "Norbert Wozniak (Dowódca) — Accountable"
architecture: "docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md"
campus_foundation: "docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md"
lanes_appendix: "docs/ops/PROGRAM-LANES-SOT.md"
scorecard: "docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md"
runtime_changes_allowed: false
budget_freeze_until: "2026-08-06"
prod_tip: "FINAL DEPLOY PASS · cache vhq-w67a · seal FINISHED_PARTIAL_LOOP"
runtime_commit: "prod tip of record via todo.gate_machine.prod_tip"
cache_asset: "vhq-w67a"
active_gate_pointer: null
inspiration_only: "Talk&Buy store — spatial UX inspiration; no copy"
---

# FlexGrafik Virtual HQ — Program

## 1. Business goal

> **Director can understand, control and improve the automated company through an interactive virtual HQ without guessing.**

North Star: ≤30 seconds in Mission Control to answer money / risk / decisions / lagging dept / failed agent / next action / untrusted gaps.

### Founder product direction (2026-07-27 · W1 CLOSE)

> Virtual HQ becomes the primary operational dashboard.  
> Commander is the underlying control, data, audit and action engine.  
> Existing dashboard content must progressively be reorganized into Mission Control and department Work Views, **not duplicated**.

W1-SHELL: **CLOSED** (local `vhq-w01b`). W2+ not auto-activated.

---

## 2. Non-goals / STOP

| STOP | Rule |
|------|------|
| Decorative game / fake 3D office | always |
| Copy Talk&Buy code/assets/branding/UI | always |
| Second disconnected app / duplicate data plane replacing Commander engine | always — VHQ is primary UX; Commander remains SoT engine |
| Chatbot-only “HQ” | always |
| Static room labels without Work View path | always |
| Uncontrolled agent-to-agent chat as workflow | always |
| Fake LIVE / fake KPI / fake busy agents | always |
| 6th primary Commander tab (D0.15) | always |
| SSO / iframe merge OS↔jadzia | always |
| 3D before dogfood proves value | until VF-VHQ-3D-PARKED unpark |
| Ads / paid Meta | until **2026-08-06** + GO |
| Mollie LIVE / Purchase / Gate D | separate Founder GO |
| Deploy without Zasada 11 GO | always |
| Auto-start all rooms / all VHQ waves in one session | always |
| Edit MKT dirty files in VHQ plan/design sessions | default |
| Activate VF-CAMPUS-W4 automatically | VHQ supersedes product vision; Campus W4 remains parked residual |

---

## 3. What Campus already solved (foundation to keep)

| Wave | Solved |
|------|--------|
| **W1 Navigate** | Floor·room hop labels on Mission Control map; no 6th tab |
| **W2 Trust** | Hop Contracts + honest LIVE/PARTIAL/UNVERIFIED/PARKED badges + evidence IDs |
| **W3 Truth Cards** | 5 read-only cards: status + SoT + primary action + insufficient_data rule |
| **Deploy** | Prod tip **`014c791`** · runtime **`06212d7`** · cache URL **`vhq-w60a`** · W6 Approval Vault **path DEPLOYED** · room maturity **PARTIAL** |

Campus = **truthful control foundation**. It is **not** the interactive Virtual HQ product vision.

---

## 4. What Campus does NOT solve (product gap)

- Spatial “enter the company” experience (World View)
- Director Command View answering 7 questions in ≤30s as a designed loop
- Typed Operations Bus across departments
- Room Work Views beyond map/Truth Cards
- Visual building metaphor with discoverability (Talk&Buy-class orientation, not clone)
- Unified approval vault UX for L2–L4
- Honest PLANNED shells for unfinished ops rooms without implying LIVE desks

---

## 5. Evidence Baseline (reconciled 2026-07-31 · W6 path DEPLOYED · tip `014c791` · cache `vhq-w60a`)

| System / room | Current reality | SoT | Status | Evidence | Can appear in HQ? |
|---------------|-----------------|-----|--------|----------|-------------------|
| Mission Control | Commander Home LIVE | `commander/?v=vhq-w60a` | **LIVE** | EV-W2-001 · tip 014c791 | **Yes — MVP core** |
| Boardroom | docs strategy | flexgrafik-meta master-plan | PARTIAL | docs | Yes — later |
| Approval Vault | Ops Bus Vault Work View (`?vhq=approval-vault`) · pending `approval_needed` | `ops_bus_events` · Audyt secondary | **PARTIAL** | EV-W6-001 · EV-W2-009 historical | Yes — MVP thin |
| AI / Agent Health | DA OK · worker SSH ok (INC-SSH CLOSED 2026-07-31) | health APIs · Agenci | **PARTIAL** (OS/VCMS post-auth) | EV-W2-006 · INC-SSH-RECOVERY-00 CLOSE | Yes — MVP |
| Agent OS | hop challenge; post-auth unseen | os.flexgrafik.nl | PARTIAL | W2 residual | Pin only |
| VCMS | Conflicts claim; post-auth PARTIAL | cmd.flexgrafik.nl | PARTIAL | W2 · scan | Pin only |
| Knowledge | docs / Basic Auth body unseen | KNOWLEDGE index · cmd docs | UNVERIFIED | W2 | Later |
| Analytics / Finance | Analityka tab path | Commander analytics | **UNVERIFIED** | EV-W2-008 | Yes — honest |
| Compliance | Settings→Audyt | AGENTS parks | PARTIAL | EV-W2-009 | Later |
| Data & AI Lab | MB rail propose-only | Marketing rail | PARTIAL | MB exists | Later |
| Reception / Widget | REV-DEMAND LIVE | widget / TG | LIVE capability | REV-DEMAND | Later shell |
| Sales queue | Home CRITICAL/ACTION | jadzia tickets | **LIVE** | REV-DEMAND | **Yes — MVP via MC** |
| Wizard / Quote | SPA Stap 1–9 | zzpackage `/wizard/` | **LIVE** | EV-W2-005 | **Yes — MVP** |
| Marketing Studio | organic UI; campaign unverified; paid freeze | Marketing tab | **UNVERIFIED** / paid PARKED | EV-W3-001 | Yes — honest pin |
| Design Studio | DA health OK; UI in Wizard | DA health / Wizard | PARTIAL | EV-W2-006 | Later |
| Client Support | CS form | cs_followup | PARTIAL | scorecard#6 | Later |
| Order Desk | **no operational desk UI** | none (history #3149 ≠ desk) | **PARKED** | EV-W2-010 | Yes — PARKED shell |
| Production / Dispatch | no dashboard | none | PARKED / PLANNED | parks | PARKED shells |
| Asset Warehouse | MKT materials HITL; dirty local | GDrive / ASSET-PREP | PARKED (override) | MKT dirty **do not edit** | PARKED |
| Supplier Dock | roadmap | none | PARKED | VF-PARK-PROCUREMENT | PARKED |
| MKT dirty files | unstaged local | — | excluded | status --short | **Appear as PARKED only — no edit** |

---

## 6. MVP definition

**VF-VHQ MVP** = Director can:

1. Open Virtual HQ shell (2D/iso) without breaking existing 5 Commander tabs  
2. Land in **Command View** (Mission Control) and answer the 7 Director questions using **real** queue + health + Truth Cards + honest gaps  
3. Teleport to **3–5 rooms**: Mission Control, Wizard, Sales (queue), Approval Vault (thin), AI Health  
4. See World pins for Marketing / Order Desk / Finance with **honest** UNVERIFIED/PARKED  
5. Never invent desks, KPIs, or busy agents  

**Out of MVP:** full P0 production spine UI, 3D, Ads, Mollie, all rooms polished, full Ops Bus catalog beyond cash spine.  
**W5 LIVE (2026-07-31):** typed cash-spine bus `lead_qualified` → `wizard_started` → `order_created` + audit/L2–L3 STOP · tip `67700ff` · cache `vhq-w50a` · Order Desk remains PARKED EV-W2-010.  
**W6 (2026-07-31):** Approval Vault **path DEPLOYED** · room maturity **PARTIAL** · tip `014c791` · runtime `06212d7` · cache `vhq-w60a` · L2 Approve flips **companion** `approval_needed` only (parent may stay pending) · L3/L4 STOP · Order Desk remains PARKED EV-W2-010.

---

## 7. Phased implementation plan

| Gate | Intent | Type | Depends |
|------|--------|------|---------|
| **VF-VHQ-PLAN-00** | This program + architecture + backlog | docs | Founder GO (done this session) |
| **VF-VHQ-DESIGN-00** | IA wireframes, room YAML sketch, shell ADR, bus schemas | docs/design | PLAN-00 |
| **VF-VHQ-W1-SHELL** | 2D/iso World shell + teleport; no fake LIVE | UI-only | DESIGN-00 + GO |
| **VF-VHQ-W2-MISSION-CONTROL** | Command View 7-question loop bound to real data | UI + read APIs | W1 |
| **VF-VHQ-W3-ROOMS-COMMERCIAL** | Work Views: Wizard/Sales/Marketing pins honest | UI + deeplinks | W2 |
| **VF-VHQ-W4-ROOMS-OPERATIONS** | PARKED/PLANNED ops shells + Order Desk path when SoT exists | UI (+ data if SoT) | W2; Order LIVE needs SoT |
| **VF-VHQ-W5-OPERATIONS-BUS** | Typed events/tasks + audit (no agent chat) — **CLOSED+DEPLOY tip `67700ff` / `vhq-w50a`** | data integration | W2+ schemas |
| **VF-VHQ-W6-DIRECTOR-APPROVALS** | Approval Vault L2–L4 UX — **CLOSED+DEPLOY tip `014c791` / runtime `06212d7` / `vhq-w60a`** · maturity PARTIAL | UI + action risk | W5 + GO per class |
| **VF-VHQ-W7-DOGFOOD** | Director ≤30s dogfood + evidence — **CLOSED PASS 2026-07-31** · 994ms · `vhq-w60a` | verify | W2 min; prefer W6 |
| **VF-VHQ-UX-AUDIT-00** | Interaction UX audit + P0/P1 fix — **CLOSED+DEPLOY PASS 2026-07-31** · tip `a49644c` · cache `vhq-w61a` | verify → UI | W7 |
| **VF-VHQ-P2-SNR-00** | Decision Rail SNR Wave 1 — **CLOSED+DEPLOY PASS 2026-07-31** · tip `7e34940` · cache `vhq-w62a` | API+UI | UX-AUDIT |
| **VHQ-DI scorecard** | Decision Instrument S1–S6+S8 = **5 DONE** · S7 parked — SoT `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md` · lanes `docs/ops/PROGRAM-LANES-SOT.md` · **ACTIVE** `VF-VHQ-FINAL-00` (nav F7) | program | runtime `adafd83` / cache target `vhq-w67a` |
| **VF-VHQ-3D-PARKED** | True 3D | parked forever until unpark | W7 PASS + Founder |

**Campus W4** stays **parked** (UNIT-ECONOMICS hint / Order deep-link residual). Product path = VHQ gates.

---

## 8. Dependencies

| Dependency | Impact |
|------------|--------|
| Commander tip `014c791` · runtime `06212d7` · cache `vhq-w60a` · ops_bus_events + Approval Vault (PARTIAL) | MVP data surface + W5/W6 |
| JWT session | queue / audit / analytics freshness |
| INC-SSH-RECOVERY-00 | **CLOSED** 2026-07-31 — prod `ssh_connection=ok` |
| Order Desk SoT | blocks LIVE ops room |
| Finance session/DTL | blocks LIVE finance |
| MKT-ASSET-00 / freeze | Marketing remains UNVERIFIED/PARKED |
| Agent OS / VCMS auth | post-auth PARTIAL pins |
| Zasada 11 | every deploy |

---

## 9. Risks

| Risk | Mitigation |
|------|------------|
| Building décor slows work | Command View default on mobile; teleport mandatory |
| Scope explosion (all rooms) | MVP = 3–5 rooms; placeholders honest |
| Fake digital twin | Evidence rules from Campus; insufficient_data |
| Bus becomes chat | Typed events only; DESIGN schemas |
| Parallel Campus W4 vs VHQ confusion | W4 parked; VHQ = product vision |
| MKT dirty bleed into commits | Explicit exclude lists |
| 3D premature | 3D gate parked |

---

## 10. RACI

| Decision | R | A | C | I |
|----------|---|---|---|---|
| CLOSE PLAN-00 | Architect/agent | **Dowódca** | Ops | sztab |
| Activate DESIGN / W1 | agent prep | **Dowódca** | Ops | — |
| Room LIVE badge | room owner | **Ops/COI** | Security | Founder |
| Bus event schema | architect | **Ops/COI** | Security | — |
| L3/L4 approvals | proposer | **Dowódca** | Ops/Sec | — |
| Deploy HQ UI | agent | **Dowódca** | Ops | — |
| Unpark 3D | — | **Dowódca** | Ops | — |

---

## 11. Definition of Done — VF-VHQ-PLAN-00

- [x] Architecture doc with full room registry + Ops Bus + 2D-first + 3D parked  
- [x] Program doc with goal, non-goals, evidence baseline, MVP, phases, RACI, STOP  
- [x] todo.json registers all VHQ gates (not auto-implementing)  
- [x] Mermaid/SVG blueprint in architecture  
- [x] Handoff CLOSE  
- [x] No commander-ui / app.js / deploy / commit / MKT edits  

---

## 12. Proposed control-plane decision (HITL — not auto-applied beyond PLAN register)

```text
RECOMMEND:
  active_gate → VF-VHQ-PLAN-00 (completed this session)
  proposed_next_gate → VF-VHQ-DESIGN-00 (NOT active)
  VF-CAMPUS-W4 remains parked
  MKT-ASSET-00 remains parked_by_founder
DO NOT auto-start DESIGN or W1-SHELL without separate Founder GO.
```

---

## 13. References

- Architecture: [FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md](./FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md)  
- Campus program (foundation): [FLEXGRAFIK-CAMPUS-PROGRAM.md](./FLEXGRAFIK-CAMPUS-PROGRAM.md)  
- Campus map: [FLEXGRAFIK-CAMPUS-MAP.md](./FLEXGRAFIK-CAMPUS-MAP.md)  
- Prod Commander: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a  
- Inspiration only: https://store.talknbuy.com/pl/
