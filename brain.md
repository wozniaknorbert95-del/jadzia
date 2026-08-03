---
status: "[ACTIVE]"
title: "Jadzia-Core Brain (Canonical)"
owner: "Norbert Wozniak"
updated: "2026-08-03"
readiness_overall: "Etap 5f SEALED; Hard DoD 15/15; TOOL 100% SEALED; live P0 PARKED; awaiting Dowódca unlock"
---

## 1) Misja modułu

**TO-BE (wizja):** Jadzia jako **Chief Operating Intelligence (COI)** — prawa ręka Dowódcy: sense → think → plan → act → guard (Kaizen).

**AS-IS (dziś, uczciwie):** FastAPI backend na VPS z filarami LIVE:
- WP code agent (SSH read/write/rollback) via Telegram + worker queue + HITL
- Customer sales chat widget dla Wizarda (INT-001)
- Task/session management w SQLite (`jadzia.db`)
- **COI Commander** (queue, Marketing, audit, JWT) — prod 2026-07-09
- **Content Intake M1 + Publish Hardening B** — FB text/photo z GDrive URL

Szczegóły charter: `flexgrafik-meta/docs/core/jadzia-operating-charter.md`

## 2) AS-IS LIVE (kod potwierdzony, 2026-06-30)

| Capability | Entry point | Status |
|------------|-------------|--------|
| WP edit pipeline | `core/agent.py` → `agent/nodes/*` → SSH | LIVE |
| Worker queue + HITL | `api/routes/worker.py`, JWT | LIVE |
| Wizard widget chat | `POST /api/v1/widget/chat` | LIVE (+ Wizard CTA deeplink; durable lead on email+consent) |
| Telegram ops | `api/telegram.py` | LIVE |
| LLM client | `core/llm.py` (Haiku/Sonnet) | LIVE |
| Session state | `agent/state/` + `agent/db.py` | LIVE (SQLite-only) |
| Cost tracking | `api/routes/costs.py` | LIVE |
| Content calendar | `agent/nodes/content_calendar_node.py` | LIVE |
| Weekly COI brief | `agent/nodes/brief_node.py` | LIVE (worker hook + HITL draft tickets) |
| Portal qualification | `api/routes/portal_qualify.py` | LIVE (INT-012) |
| **Management CLI** | `cli/main.py` → `jadzia` cmd | LIVE (5 cmds) |
| Design Agent INSPIRE v2/enterprise | `api/routes/design_agent*.py` + `agent/inspire/` | LIVE (merge `46e4fc2` 2026-07-17) |
| **COI Commander** | `commander-ui/` + `api/routes/commander.py` | LIVE (master merge + VPS 2026-07-09; SMTP Delegat eskalacja LIVE 2026-07-17) |
| **Marketing intake** | `commander-ui` Marketing + `agent/media/gdrive.py` | LIVE (M1 + M2 video E2E PASS 2026-07-17) |
| Facebook photo publish | `agent/publishers/facebook.py` `publish_photo` | LIVE (entry #16 QR + smoke 2026-07-17) |
| Facebook video publish | `agent/publishers/facebook.py` `publish_video` | LIVE (entry #21 `fb_post_id=1483779380183430`) |

**Pipeline:** `routing → commands | intent | planning | generate | approval → SSH write → HITL diff`

**VPS runtime:** `jadzia` user (non-root), `/opt/jadzia`, systemd `jadzia.service`

## 3) COI Phase A (kod agenta — COMPLETE)

| Element | Kontrakt | Status |
|---------|----------|--------|
| Order ingestion | INT-002 `POST /webhooks/woocommerce/order` | v1+v2 LIVE @ `504fdf6`; producer @ `bfe8485`; Gate C PASS (#3209 test); COD OFF; Gate D parked (no top-up); min199 unchanged |
| `order_node` | `agent/nodes/order_node.py` | LIVE |
| `orders` table | `jadzia.db` — `agent/db.py` | LIVE v1; additive v2 evidence migration tested |
| Lead ingestion | INT-004 `POST /api/v1/leads` | LIVE (DEPLOY-02 E2E PASS) |
| `lead_node` | `agent/nodes/lead_node.py` | LIVE |
| `leads` table | `jadzia.db` | LIVE |
| Analytics snapshot | INT-009 `GET /api/v1/analytics/snapshot` | LIVE (GA4 on VPS; prod-smoke 8/8) |
| `analytics_node` | `agent/nodes/analytics_node.py` | LIVE |
| Content calendar | INT-010 `GET/POST/PATCH /api/v1/content-calendar` | LIVE (VPS) |
| `content_calendar_node` | `agent/nodes/content_calendar_node.py` | LIVE |
| Facebook publish | INT-011 `POST/GET …/publish` | LIVE (text/photo/video; PAGE token `expires_at=0` 2026-07-17) |
| Commander Marketing | composer + GDrive + failed UX | LIVE (M1 + Phase B) |

Plan Phase A (completed): `docs/archive/plans/PLAN-COI-PHASE-A.md`  
Plan Phase B (completed): `docs/archive/plans/PLAN-COI-PHASE-B.md`

## 4) Dane

- **Operational SSoT:** `data/jadzia.db` (SQLite-only — brak JSON session files)
- **Agent tasks/sessions:** `agent/db.py`, `agent/state/`
- **Customer chat:** TTLCache (L1) + `widget_chat_sessions` SQLite (L2, TTL 24h) — REV-DEMAND-02; `created_at` set-once (OPS-AI-01 v1.1 AI-ops clock)
- **Orders/leads:** LIVE w `jadzia.db` (Phase A kod)
- **Analytics:** GA4 read-through cache + **SQLite persist** (`analytics_snapshots`, S3-01)
- **Content calendar:** LIVE w `jadzia.db` (Phase B bootstrap)

## 5) Integracje

| ID | Kierunek | Status |
|----|----------|--------|
| INT-001 | Wizard → widget chat | LIVE |
| INT-002 | WC → order webhook | v1+v2 LIVE @ `504fdf6`; Gate C PASS; Gate D deferred |
| INT-003 | Game → Wizard coupon | LIVE (app side) |
| INT-004 | app → `POST /api/v1/leads` | LIVE (DEPLOY-02 E2E PASS) |
| INT-009 | GA4 → analytics snapshot | LIVE |
| INT-010 | Content calendar | LIVE (VPS) |
| INT-011 | Facebook publish | LIVE (VPS E2E 2026-07-01) |
| INT-012 | Portal qualification | LIVE (2026-06-25) |

Pełne kontrakty: `flexgrafik-meta/docs/core/integration-contracts.md`

## 6) Readiness vs wizja COI

| Dimension | AS-IS | TO-BE |
|-----------|-------|-------|
| WP SSH agent | 90% | 95% |
| Customer chat | 85% | 90% |
| Worker queue/HITL | 90% (brief→Commander HITL tickets) | 90% |
| Operational OS (orders/leads) | 90% (INT-002 v2 + Gate C; Gate D parked) | 90% |
| Analytics integration | 80% | 80% |
| Content calendar | 90% (intake + photo/video publish) | 95% |
| COI Commander | 92% (tickets from brief HITL) | 95% |
| COI strategy synthesis | 65% (brief LIVE + HITL draft spawn; no auto-act) | 85% |
| **Overall** | **~93%** operational spine | **85%** full COI vision |

**Honest bar:** AS-IS meets agent-achievable TO-BE without money/secrets/TikTok. Remaining gaps: Gate D LIVE proof, strategy auto-spawn (INT-006), content 95%, Commander 95%, S1-01 BFG.

## 7) Source of Truth

**Hierarchia (Knowledge Index):** meta rules → **`todo.json`** → ops programs → handoffs (ephemeral).

- **Knowledge Index:** `docs/ops/KNOWLEDGE-SYSTEM-INDEX.md`
- **Control plane / backlog:** `todo.json` (`active_gate`, `next_*`)
- **Product program (ACTIVE):** `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md`
- **Campus program:** `SUPERSEDED` — `docs/ops/FLEXGRAFIK-CAMPUS-PROGRAM.md` (foundation only)
- **DI scorecard:** `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md` (S3–S6+S8 DONE; S7 parked)
- **Lanes appendix:** `docs/ops/PROGRAM-LANES-SOT.md` (ściąga — nie plan)
- **Demand OS / Biuro Popytu (program faz):** `docs/ops/demand-os/PROGRAM-PHASES.md`
- **Etap 5f MASTER TODO:** `docs/ops/demand-os/MASTER-TODO-5F.md` · SEALED 2026-08-03 · design `DEMAND-CONTROL-PANEL-DESIGN.md` · API `DESK-CONTRACT.md`
- **Primary Commander surface:** `#view-demand-desk` (Biuro Popytu)
- **Marketing HITL:** TOOL 100% SEALED · live `4-P0-*` PARKED · unlock = Dowódca only · rule `.cursor/rules/demand-os-tool-first.mdc`
- **OS TARGET (Demand Machine):** `docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`
- **Tool coherence:** `docs/ops/demand-os/OS-TARGET-COHERENCE.md` (Etap 1 SEALED)
- **Module spec (COI):** `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`
- **Charter:** `flexgrafik-meta/docs/core/jadzia-operating-charter.md`
- **Globalne zasady:** `flexgrafik-meta/docs/core/global-rules.md` (VCMS = pointer)
- **Workflow:** `.agents/workflows/README.md` → start `/vibe-init`
- **PRD:** `docs/PRD-core.md`
- **Prod tip:** `a3deb59` (OPS HARDENING SEAL) · cache `desk-dash09` (UX repair local; prod after GO deploy)
- **Handoffs LIVE:** `docs/handoffs/` (≤15; cold → `docs/archive/handoffs/`)

## 8) Workflow Framework (v2.2)

Golden Path: **L0 Triage → L3 Validate → L3.5 Post-coding → L4 Handoff/Deploy**

| Layer | Komenda | Cel |
|-------|---------|-----|
| L0 | `/vibe-init` | Triage, klasyfikacja |
| L3 | `/jadzia-test` | Pytest + smoke |
| L3–L4 | `/vhq-decision-instrument` | DI scorecard (idle — closeout DONE) |
| L3.5 | `/post-coding` | Validate → ship pack |
| L4 | `/jadzia-deploy` | VPS tylko z GO |
| L4 | `/handoff` | Zamknięcie sesji |

## 9) Guardrails

- Deploy produkcja: **manual** (Zasada 11)
- Zasada 1-1-1: jedna sesja = jedno zadanie = jeden handoff
- Brak commitu w repo produktowych przez COI runtime (to Cursor/Agent OS)
- Min checkout 199 EUR, marża 60% — Wizard-only

## 10) Context Packet (sesja agenta)

```
brain.md
todo.json
docs/ops/demand-os/PROGRAM-PHASES.md
docs/ops/demand-os/DEMAND-CONTROL-PANEL-DESIGN.md
docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md
docs/PRD-core.md
.agents/workflows/README.md
flexgrafik-meta/docs/core/jadzia-operating-charter.md
Latest docs/handoffs/README.md (then last 2 dated handoffs)
```
