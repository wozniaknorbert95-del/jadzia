---
status: "[BLAST]"
title: "VF-VHQ-W4-ROOMS-OPERATIONS — BLAST (honest ops shells)"
updated: "2026-07-31"
gate: "VF-VHQ-W4-ROOMS-OPERATIONS"
founder_go: true
prod_baseline: "de10e83 / vhq-w32a"
cache_target: "vhq-w40a"
commit: false
deploy: false
---

# BLAST — VF-VHQ-W4-ROOMS-OPERATIONS

**Date:** 2026-07-31  
**Backlog:** `VF-VHQ-W4-ROOMS-OPERATIONS`  
**Class:** Feature — Commander UI (static `commander-ui/`)  
**Surface (1-1-1):** P0 ops Work Views only — Order / Production / Preflight / Dispatch  
**Founder GO:** explicit in session (`/vibe-init → GO W4 → blast`)  
**Prod baseline (unchanged until deploy GO):** tip `de10e83` · cache `vhq-w32a`

---

## B — Background (Why)

| Field | Value |
|-------|-------|
| Trigger | Session close W3.2 LIVE + TG fix; W4 parked until Founder GO; GO received 2026-07-31 |
| Value | Director teleports to P0 ops rooms and sees **honest** PARKED/PLANNED shells — never a fake Order Desk |
| Program SoT | `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` §7 W4 |
| Prior | W3.2 CLOSE · `VHQ_ROOMS` sole SoT · cache `vhq-w32a` |
| Honesty residual | Order Desk **PARKED** **EV-W2-010** — preserve until real desk SoT exists |

**Data flow (no new API / no Order SoT invent):**  
Browser → HQ floor P0 → teleport room → Work View panel bound from `VHQ_ROOMS` → status / evidence / limitation / KPI=`insufficient_data` → no LIVE KPI path.

INT-002 orders table may exist in SQLite — **out of W4 scope**. Historical #3149 ≠ live desk. No dashboard invented from DB rows.

---

## L — Limits & invariants

### In scope

- Honest Work View shells for:
  - `order-desk` → **PARKED** · **EV-W2-010** (must remain)
  - `production-control` → **PARKED** (shell; Erka HITL only — no invented production board)
  - `preflight-quality` → **PLANNED**
  - `dispatch-returns` → **PARKED** (align `VF-PARK-DISPATCH`)
- Bind chrome from `VHQ_ROOMS` only (eyebrow, status, evidence, SoT label, limitation, KPI insufficient_data)
- Wizard → Order handoff button continues to open Order Work View (still PARKED)
- Ops flow strip / Pulse / Truth Card Order remain consistent
- Cache bump local → **`vhq-w40a`**
- `todo.json` gate activation + `preserved_w4` after CLOSE

### Out of scope / Hard STOP

- **No fake Order Desk LIVE**
- **No invented production / dispatch dashboard or KPIs**
- No 6th Commander tab · no 3D · no second status SoT (`VHQ_PULSE` stays dead)
- No Ads / Mollie / Gate D / MKT dirty touch / commit of `docs/ops/marketing/**`
- No Python routes / schema / Operations Bus (that's W5)
- No auto-deploy (Zasada 11) — deploy needs separate GO after CLOSE
- No Campus W4 activation (`VF-CAMPUS-W4` stays parked)
- Do not flip Order to LIVE even if `orders` table has rows

### Invariants to protect (W1–W3.2)

- `VHQ_ROOMS` sole SoT
- HQ primary · Console secondary · Return to HQ first
- Five tabs · single `#queue-list`
- Primary + legacy shell modes
- Marketing UNVERIFIED EV-W3-001 · SSH DEGRADED EV-W2-011
- Commercial handoff: Sales LIVE → Wizard LIVE → **Order PARKED EV-W2-010**
- Esc ladder · floor filter · focus trap

---

## A — Actions (`/implement`)

### A1 Manifest honesty (`commander-ui/app.js` · `VHQ_ROOMS`)

- [ ] Confirm `order-desk.status="PARKED"` · `evidence="EV-W2-010"` · KPI `insufficient_data` · `action=null`
- [ ] Tighten `production-control` / `preflight-quality` / `dispatch-returns`: clear limitation, owner, sotLabel; optional evidence tags `EV-W4-001`/`EV-W4-002`/`EV-W4-003` **only as shell honesty IDs** (not LIVE claims)
- [ ] Add `honesty[]` banners (Marketing pattern) for each ops room
- [ ] Ensure `floorCard: true` + teleport opens Work View (not Console fake desk)

### A2 Work View panels (`commander-ui/index.html`)

- [ ] Add four panels under `#vhq-work`:
  - `data-vhq-work="order-desk"`
  - `data-vhq-work="production-control"`
  - `data-vhq-work="preflight-quality"`
  - `data-vhq-work="dispatch-returns"`
- [ ] Each: eyebrow · Director Q (honest) · honesty banners · meta dl · Back to MC · **no primary CTA that implies LIVE desk**
- [ ] Order panel: explicit copy “operational desk not implemented · EV-W2-010”
- [ ] Cache query `styles.css` / `app.js` → `vhq-w40a`; body `data-vhq-w4="1"`

### A3 Bind + navigate (`commander-ui/app.js`)

- [ ] Extend `vhqBindWorkViews()` for the four rooms (mirror Marketing honesty bind)
- [ ] Room open path shows Work View when panel exists; panel chrome from manifest
- [ ] Wizard Order handoff button → Order Work View PARKED (already wired; verify)
- [ ] Truth Card Order action text: drop stale “W4 deep-link after C2” → “None — desk not implemented (EV-W2-010)”
- [ ] Ops flow break hint stays Order PARKED

### A4 Styles (`commander-ui/styles.css`)

- [ ] Reuse W3 honesty banners / work-meta; minimal P0 polish only if needed
- [ ] No new card-dashboard look that reads as LIVE ops

### A5 Evidence / backlog

- [ ] Local dogfood checklist → PRECLOSE handoff
- [ ] `todo.json`: gate `in_progress` now; `completed` only after Founder CLOSE
- [ ] CLOSE + optional COMMIT (exclude MKT) + DEPLOY only with separate GO

---

## S — Success criteria (DoD)

Binary:

- [ ] All four ops rooms open an in-HQ Work View labeled **PARKED** or **PLANNED** (never LIVE)
- [ ] **EV-W2-010** visible on Order Desk (floor · Work View · Truth · Wizard handoff · flow break)
- [ ] Zero fabricated open-order / SLA / production / dispatch KPIs (only `insufficient_data` or explicit parked copy)
- [ ] No new API · no Order SoT invented · no 6th tab · no MKT touch
- [ ] W3.2 invariants preserved (sole SoT, HQ primary, Console secondary, 5 tabs, legacy)
- [ ] Cache `vhq-w40a` local dogfood PASS
- [ ] PRECLOSE ready for Founder dogfood → CLOSE

---

## T — Test plan

| Layer | What |
|-------|------|
| Static | Open local Commander `?v=vhq-w40a` · JWT optional (ops shells must work without inventing queue data) |
| Teleport | P0: Order / Production / Preflight / Dispatch → Work View honesty |
| Cross-surface | Order status identical on floor card, panel, Truth Card, Wizard handoff, flow strip |
| Negative | No LIVE badge · no numeric fake KPI · no Ads/Mollie path |
| Regression | MC cold-open · Sales/Wizard/Marketing Work Views · Console secondary · `?vhq_shell=legacy` |
| Manifest probe | Existing `vhqManifestPropagationTest` still green if present |

---

## Decision (senior · no-ask)

**Path:** UI-only honest shells. Do **not** wire INT-002/`orders` into a desk in W4 — that would fake LIVE without an operational SoT contract. Real Order Desk LIVE = later gate after SoT + Founder GO.

---

## Staging list (W4-only — after implement, HITL commit)

```text
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
todo.json
docs/handoffs/2026-07-31-VF-VHQ-W4-ROOMS-OPERATIONS-BLAST.md
docs/handoffs/2026-07-31-VF-VHQ-W4-ROOMS-OPERATIONS-PRECLOSE.md  (later)
```

**Never stage:** `docs/ops/marketing/**`, MKT assets, unrelated deploy handoffs unless separate GO.

---

BLAST_VERDICT: **ANCHORED** — ready for `/implement`
