# VF-VHQ-W1-SHELL — CLOSE

**Date:** 2026-07-27  
**Gate:** `VF-VHQ-W1-SHELL`  
**Decision:** **CLOSED** — Founder approved W1 polish  
**Cache (local):** `vhq-w01b`  
**Local URL:** `http://127.0.0.1:8765/index.html?v=vhq-w01b`  
**Prod tip (unchanged):** `3487ec0` / `campus-w03` — **no deploy this close**  
**Commit:** **not performed** (HITL)  
**W2:** **not activated** (`proposed_next_gate_active: false`)

---

## Founder product direction (recorded)

> Virtual HQ becomes the primary operational dashboard.  
> Commander is the underlying control, data, audit and action engine.  
> Existing dashboard content must progressively be reorganized into  
> Mission Control and department Work Views, not duplicated.

Also written into `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md` §0.

---

## Final W1 Definition of Done

| # | Criterion | Status |
|---|-----------|--------|
| 1 | Overlay Virtual HQ inside Commander (no 6th tab, no new app) | PASS |
| 2 | Floors P3–MAG + room grid; MVP rooms interactive | PASS |
| 3 | Honest status chips LIVE / PARTIAL / UNVERIFIED / DEGRADED / PARKED / PLANNED + evidence IDs | PASS |
| 4 | Teleport / room panel / primary actions only to real SoT or explicit PARKED | PASS |
| 5 | Mission Control default **only** on initial HQ entry | PASS |
| 6 | Floor click filters floor — **does not** auto-open first room | PASS (Founder polish) |
| 7 | Opaque HQ overlay — Commander not visually competing | PASS (Founder polish) |
| 8 | Modal focus trap; Tab/Shift+Tab stay in dialog; Esc closes; focus → `#vhq-enter` | PASS (Founder polish) |
| 9 | Dogfood A–J + P1 no-Reception auto-open | PASS |
| 10 | No Ads / Mollie / 3D / MKT publish / W2 auto / secrets | PASS |
| 11 | Founder visual approval of polish | PASS — CLOSE |

**Preserved invariants (must survive future gates):**
- opaque Virtual HQ overlay  
- floor filtering without auto-opening first room  
- proper modal focus trap  
- Esc close + focus restore to Enter Virtual HQ  
- honest status/evidence model  
- no sixth Commander tab  

---

## Exact changed close files (this CLOSE action)

| File | Role |
|------|------|
| `todo.json` | Gate → `completed`; `active_gate` cleared; W2 stays parked |
| `docs/handoffs/2026-07-27-VF-VHQ-W1-SHELL-CLOSE.md` | This CLOSE record |
| `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md` | Founder product direction §0 |
| `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` | Founder product direction §1 + STOP clarify |

**W1 implementation already present (preserve, do not revert):**
| File | Role |
|------|------|
| `commander-ui/index.html` | Entry + shell markup · cache `vhq-w01b` |
| `commander-ui/styles.css` | Opaque shell + mobile list + backdrop inert |
| `commander-ui/app.js` | Open/close/teleport/floor browse/focus trap/Esc |
| `docs/handoffs/2026-07-27-VF-VHQ-W1-SHELL-PRECLOSE.md` | Pre-close (implementation) |
| `docs/handoffs/2026-07-27-VF-VHQ-W1-SHELL-POLISH-PRECLOSE.md` | Polish dogfood |

**Explicitly NOT touched:** MKT paths, `ASSET-MATERIALS-PREP.md`, `OPERATOR-TODAY.md`, Campus deploy handoffs, any other dirty unrelated worktree files.

---

## Git diff summary (W1 scope only — at CLOSE)

Approximate (excludes MKT):

| Path | Δ |
|------|---|
| `commander-ui/app.js` | ~+650 (VHQ shell logic + polish) |
| `commander-ui/index.html` | ~+121 / −2 |
| `commander-ui/styles.css` | ~+243 |
| `todo.json` | gate machine + W1 → completed |
| `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md` | Founder direction |
| `docs/handoffs/2026-07-27-VF-VHQ-W1-SHELL-*.md` | PRECLOSE / POLISH / CLOSE |

**Not in recommended commits:** `docs/ops/marketing/**`, `MKT/**`, Campus W2/W3 deploy CLOSE handoffs unless Founder separately requests.

---

## Recommended atomic commit list (HITL — do not run yet)

1. **`feat(vhq): add W1 Virtual HQ shell overlay`**  
   - `commander-ui/index.html`  
   - `commander-ui/styles.css`  
   - `commander-ui/app.js`  

2. **`docs(vhq): close VF-VHQ-W1-SHELL`**  
   - `todo.json`  
   - `docs/handoffs/2026-07-27-VF-VHQ-W1-SHELL-PRECLOSE.md`  
   - `docs/handoffs/2026-07-27-VF-VHQ-W1-SHELL-POLISH-PRECLOSE.md`  
   - `docs/handoffs/2026-07-27-VF-VHQ-W1-SHELL-CLOSE.md`  
   - `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-ARCHITECTURE.md`  

Optional later (separate GO): **`chore(deploy): VHQ W1-SHELL to prod`** — only with explicit deploy GO + tip verify.

---

## Proposed W2 scope — Virtual HQ as primary dashboard

**Gate (parked until GO):** `VF-VHQ-W2-MISSION-CONTROL`

**Goal:** Mission Control becomes the **Command View** that progressively **absorbs** existing Commander Home dashboard content (priorities, queue, system health, Truth Cards) — **reorganize, do not duplicate**.

### In scope (proposed)
1. **Primary entry:** cold-open path prefers Virtual HQ → Mission Control (Home entry remains; no 6th tab).  
2. **Mission Control Work View:** bind Director questions to real SoT already on Home (`#priorities`, `#queue-list`, SSH/INC, Truth Cards) via panels or embedded sections — single surface, no cloned KPI widgets.  
3. **Reorganization plan (incremental):** map each Home block → MC or department room Work View; hide/relocate on Home only after MC equivalent proven.  
4. **Honest gaps:** `insufficient_data` / DEGRADED preserved (e.g. SSH INC); never invent LIVE Order Desk.  
5. **≤30s Director dogfood** checklist with evidence IDs.

### Out of scope (W2)
- New rooms beyond existing shell  
- Operations Bus / Approval Vault write flows (W5/W6)  
- Ads / Mollie / 3D / 6th tab  
- Auto-commit of MKT dirty tree  
- Inventing Order Desk LIVE  

### Exit
Founder dogfood PASS → CLOSE W2 → separate commit/deploy GO.

---

## Stop conditions honoured

- No commit  
- No deploy  
- No auto-activate W2  
- No MKT modifications  
- `standing_go_closeout` remains `false`  

**Next HITL:** approve commits → optional deploy GO → decide `GO VF-VHQ-W2-MISSION-CONTROL` or hold.
