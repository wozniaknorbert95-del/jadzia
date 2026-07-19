# BLAST — REV-DEMAND-04 Brief HITL → sales CTA tickets

**Date:** 2026-07-18  
**Repo:** jadzia-core ONLY  
**Branch:** `master` @ `d629e1c` (local=origin; VPS tip SoT = `git rev-parse` on `/opt/jadzia`)  
**Backlog:** `REV-DEMAND-04` (F7)  
**Fundacja:** Plan1+2 LIVE + deep verify PASS (`docs/handoffs/2026-07-18-plan12-deep-VERIFY.md`)  
**Status:** BLAST anchored — ready `/implement`

## B — Background

Weekly brief HITL (`COI-STRATEGY-HITL-01`) spawns only **ops** drafts (`source=brief_hitl`: unknown orders, GA4, FB hygiene).  
Demand path already has widget CTA + lead disposition, but brief ritual does **not** produce sales action tickets in Commander.

**User value:** Dowódca opens Commander after brief → sees ≤3 **sales CTA** tickets with lead + Wizard deeplink → Ack/Snooze/Close (HITL, no auto-act).

**Flow:**
```text
send_weekly_brief()
  → collect_weekly_metrics() (+ open CTA-band leads)
  → spawn_brief_hitl_tickets()          # ops — unchanged
  → spawn_brief_sales_cta_tickets()     # NEW sales
       → propose_sales_cta_recommendations()
       → db_commander_create_ticket(source=brief_sales_cta)
  → Commander queue maps source → queue_type=sales_cta
  → UI disposition via existing POST .../leads/{id}/disposition
```

## L — Limits

- **No** Gate D / Mollie LIVE / min199 / live charge
- **No** park deletes; **no** ship `deployment/_recover_*.py`
- **No** Agent OS merge into Commander
- **No** change to widget CTA score gate (02a) or INSPIRE bridge (03)
- **No** ticket schema rewrite / new DB columns (parse `lead_id` from description or title)
- Ops `brief_hitl` codes stay; sales is additive (`brief_sales_cta`)
- Cap: `MAX_SALES_CTA_TICKETS = 3`; dedupe open titles/`lead_id`
- Deploy only after Dowódca GO (Zasada 11)
- SQLite = SSoT; logger %-style; every log with context

**Performance:** brief spawn ≤ few SQLite reads/writes; no long locks.  
**Security:** reuse `queue:act` for disposition; no new high-impact actions; no auto SSH/publish/pay.  
**Infra:** bare VPS; no new services.

## A — Actions (implement checklist)

- [ ] `agent/nodes/brief_node.py`
  - Extend metrics with `cta_leads`: open leads `game_score >= 40`, disposition ∉ {closed, snoozed}, not `is_test`, top by score (≤3)
  - Add `BRIEF_SALES_CTA_SOURCE = "brief_sales_cta"`
  - Add `propose_sales_cta_recommendations()` → codes e.g. `sales_cta_followup`
  - Titles: `[Sales CTA] Follow up lead #{id}` (+ email hint)
  - Description: lead_id, score, source, email, `cta_sku`, wizard deeplink via `build_widget_wizard_deeplink`
  - Add `spawn_brief_sales_cta_tickets()` (dedupe open source+title / lead_id)
  - Call from `send_weekly_brief()` after ops spawn
- [ ] `agent/commander/constants.py` — `sales_cta`: severity **ACTION**, SLA **4h**
- [ ] `docs/design/coi-commander/specs/D0.8-risk-matrix-sla.md` — one-row registry add
- [ ] `agent/commander/queue.py` — tickets with `source=brief_sales_cta` → `queue_type=sales_cta`; payload `{lead_id, ticket_id, wizard_deeplink?, cta_sku?}`; `available_actions` include disposition
- [ ] `commander-ui/app.js` — `leadDispositionActions` also for `sales_cta` (`payload.lead_id` / `payload.id`)
- [ ] `tests/unit/test_brief_node.py` (+ queue smoke if cheap) — no leads → 0 sales; score≥40 open → ticket; closed/snoozed skipped; dedupe; ops path still works
- [ ] `docs/ops/JADZIA-REVENUE-DOGFOOD.md` — F7 smoke line (brief spawn / queue card)
- [ ] Handoff CLOSE + `todo.json` / `brain.md` / `AGENTS.md` on finish; await deploy GO

## S — Success (DoD)

- [ ] Weekly brief path creates ≤3 open Commander tickets `source=brief_sales_cta` for CTA-band leads
- [ ] No sales tickets when no qualifying leads
- [ ] Queue surfaces them as `sales_cta` (not silent `wp_ticket`)
- [ ] Commander Home: Ack/Snooze/Close calls existing disposition API
- [ ] Ops `brief_hitl` still spawns independently
- [ ] No auto SSH / publish / pay
- [ ] `pytest` green for touched tests; `/health` unchanged
- [ ] Parks + `_recover_*.py` untouched

## T — Test plan

| Layer | Cases |
|-------|--------|
| Unit | metrics picks score≥40 open; skips closed/snoozed/test; spawn creates + dedupes; ops spawn unchanged |
| Queue | `brief_sales_cta` → `sales_cta` + lead_id in payload |
| Smoke (post-GO) | seed lead score=55 → trigger brief / spawn → Home shows Sales CTA → Ack hides from CTA band |

## Decision (senior)

**Path:** additive `brief_sales_cta` + queue `sales_cta`, CTA band `score >= 40` (align widget gate), disposition reuse.  
**Why:** fills gap between real-time `hot_lead` (≥80) and weekly sales HITL; zero schema migration; no payment surface.

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-rev-demand-04-BLAST.md
BACKLOG_ID: REV-DEMAND-04
INVARIANTS_TO_PROTECT: Gate D, Mollie, min199, parks, _recover_*.py, Agent OS merge, widget CTA gate 02a, INSPIRE 03
SUCCESS_CRITERIA: ≤3 sales_cta tickets from brief; queue+disposition; pytest green; ops brief_hitl intact
IMPLEMENTATION_PLAN: brief_node → constants/D0.8 → queue → commander-ui → tests → dogfood line → CLOSE

---
CURRENT_STAGE: L1-Design (BLAST anchored)
RECOMMENDED_NEXT: /implement
WHY_NEXT: Technical contract established; Dowódca GO already on blast
---
```
