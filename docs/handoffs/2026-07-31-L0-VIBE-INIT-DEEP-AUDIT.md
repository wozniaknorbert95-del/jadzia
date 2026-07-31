---
status: "[AUDIT]"
title: "L0 vibe-init deep audit — SoT / todo / Knowledge Index"
updated: "2026-07-31"
auditor: "agent"
mode: "read-first · executed as VF-SOT-HYGIENE-00"
tip_git: "0264f5d"
active_gate: null
follow_up: "docs/handoffs/2026-07-31-VF-SOT-HYGIENE-00-CLOSE.md"
---

# L0 Deep Audit — vibe-init + todo.json + Knowledge Index

## 0) vibe-init packet (L0)

```text
TASK_CLASSIFICATION: AUDIT (ops SoT consistency — not FEATURE/DI)
TASK_ID: none (active_gate=null · 0× in_progress tasks)
CONSTRAINTS:
  - standing_go_closeout=false → no autonomous deploy
  - runtime_changes_allowed=false
  - do not stage docs/ops/marketing/** dirty
  - Preserve EV-W2-010
INVARIANTS:
  - Knowledge Index hierarchy + conflict resolution
  - todo.active_gate is sole session steer
  - Handoffs do not override todo / constitution
RISKS:
  - Competing "ACTIVE" programs (Campus vs VHQ vs PROGRAM-LANES)
  - Handoff pile (I-6 breach) → agents read stale "next"
  - Uncommitted local tip-rewire without commit → dual truth local vs origin
READY: YES for report · NO for new feature work without Founder gate
CURRENT_STAGE: L0-Triage
RECOMMENDED_NEXT: /handoff hygiene only after GO — do NOT open Growth/S7/DI
WHY_NEXT: Chaos is SoT/metadata, not missing product code
```

---

## 1) Canonical stack (Knowledge Index — as written)

| Pri | Warstwa | Rola |
|-----|---------|------|
| 1 | flexgrafik-meta `global-rules` / workflow-manual | konstytucja |
| 2 | `brain.md` + **`todo.json`** | stan / **active_gate** |
| 3 | VCMS / cmd | governance UI |
| 4 | `docs/design/coi-commander/` | ADR |
| 5 | `docs/ops/` | runbooks, PROCESS, marketing OS, scorecards, **programs** |
| 6 | learning MBA | complete — don't regenerate |
| 7 | `docs/handoffs/` | ephemeral evidence — **nie nadpisują** 1–2 |

**Conflict resolution (Index §):**  
1 meta > brain · **2 todo > handoff** · 3 ADR > UI comment · 4 handoff updates scorecard only with evidence · …

**I-6:** rolling handoffs ≤15 lub ≤30 dni.

---

## 2) todo.json control plane — FACTS

| Field | Value | Verdict |
|-------|-------|---------|
| `active_gate` | `null` | OK — idle |
| tasks `in_progress` | **0** | OK — matches null gate |
| `closeout_queue` | `[]` | OK — DI agent queue drained |
| `standing_go_closeout` | `false` | OK — Zasada 11 |
| `runtime_changes_allowed` | `false` | OK |
| DI S3–S6+S8 | completed in `gate_machine` | OK (evidence dirs exist) |
| `closeout_blocked` | S7 `blocked_sot` EV-W2-010 | OK honesty |
| `unblocked` | `COM-AI-50-READY` | OK |
| `parked` | MKT-ASSET, Campus W4, 3D, procurement, dispatch, finance… | OK |
| `budget_freeze_until` | 2026-08-06 | OK |
| git HEAD | `0264f5d` | matches last_updated tip claim |
| origin | master synced (no ahead/behind at audit) | OK |
| **Working tree** | dirty: todo, PROGRAM-LANES*, OPERATOR-TODAY, scorecard, VHQ program, MKT/, many ?? handoffs | **FAIL hygiene** |

### Tasks of interest

| ID | status | Note |
|----|--------|------|
| COM-AI-50-READY | `unblocked` | owner Dowódca; checklist still points into **CAMPUS-PROGRAM** §14 |
| MKT-ASSET-00 | `parked` | parked_by_founder |
| INC-SSH-RECOVERY-00 | `completed` | but residuals still list ssh_degraded |
| VF-VHQ-DI-S7 | only in `closeout_blocked` | not a runnable gate |

---

## 3) Contradiction ledger (severity)

### CRITICAL — competing ACTIVE canons

| # | Conflict | A | B | Who wins per Index |
|---|----------|---|---|--------------------|
| C1 | **Two ACTIVE product programs** | `FLEXGRAFIK-CAMPUS-PROGRAM.md` status `[ACTIVE]`, `active_gate_pointer: VF-CAMPUS-W3` | `FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` `[ACTIVE]`, founder override VHQ primary | **todo** says VHQ path + `campus_w4` parked residual — Campus pointer is **STALE** but file still claims ACTIVE |
| C2 | **Third "plan of record"** | Index: plan lives in todo + ops programs | Local uncommitted: `todo.plan` / `active_plan` → **`PROGRAM-LANES-SOT.md`** (agent-invented 2026-07-31) | Lanes **not** in Knowledge Index · elevates Pri-7 style summary to Pri-2 — **protocol breach** |
| C3 | **Tip of record scatter** | git `0264f5d` / cache `vhq-w65a` / runtime `2623ae2` | VHQ-PROGRAM frontmatter still `014c791` / `vhq-w60a`; S8 CLOSE body tip `9bfa71b`; ARCHITECTURE cites `campus-w03` | Agents can deploy/dogfood wrong cache |

### HIGH — I-6 / ephemeral pollution

| # | Finding | Evidence |
|---|---------|----------|
| H1 | **Handoffs: 137 files** (+21 evidence dirs) vs I-6 ≤15 | `docs/handoffs/` count |
| H2 | Stale handoff still readable as "next" | `SESSION-HANDOFF-DI-SCORECARD-NEXT.md` says **active_gate S4** — false vs todo |
| H3 | Untracked old 2026-07-27 deploy/session closes sitting in LIVE handoffs | git `??` pile |
| H4 | Local `docs/ops/marketing/MKT/` untracked | rule: do not stage; still confuses OPERATOR path |

### MEDIUM — stale metadata inside todo / brain

| # | Finding |
|---|---------|
| M1 | `gate_machine.vhq_*_residuals` still list `ssh_degraded_inc_ssh_recovery_00` after INC-SSH **completed** |
| M2 | `campus_prod_tip` key name = Campus, value = VHQ tip |
| M3 | `brain.md` updated **2026-07-18** — no VHQ/DI; Active plan → old COI ops guide; readiness ~93% spine narrative pre-VHQ |
| M4 | Knowledge Index **Linki kluczowe** omits VHQ-PROGRAM + DI scorecard (AGENTS has DI; Index lag) |
| M5 | COM-AI checklist path still Campus PROGRAM anchor |
| M6 | AGENT `agent_rule` points at PROGRAM-LANES as kanon — overrides Golden Path wording |

### LOW — tip/doc nit

| # | Finding |
|---|---------|
| L1 | DI-S8 CLOSE frontmatter tip `9bfa71b` vs commit tip `0264f5d` (docs closeout on top of S3 runtime) — explainable but confusing |
| L2 | `.cursor/current-task.md` mirrors lanes (local only) |

---

## 4) DONE vs WAITING (from todo + evidence — not lanes invention)

### DONE (agent-capable · evidence in gate_machine)

- AI OS scorecard #1–9 LIVE (AGENTS)
- REV-DEMAND spine, Commander, marketing publish path (HITL)
- Campus W1–W3 (completed in todo; product path superseded by VHQ)
- VHQ W1–W7 + Ops Bus W5 + Vault W6 + dogfood W7
- UX-AUDIT, P2-SNR, DI **S3, S4, S5, S6, S8** = 5
- INC-SSH recovery
- `active_gate=null`, `closeout_queue=[]`

### WAITING / PARKED (honest)

| Item | Status | Real blocker |
|------|--------|--------------|
| S7 commercial loop | `blocked_sot` | Order Desk **product** SoT (EV-W2-010) — not money |
| Order / Production / Dispatch rooms | PARKED shells | same |
| COM-AI-50 | `unblocked` | Human + counsel before organic ≥2026-08-02 |
| MKT-ASSET-00 | parked_by_founder | Founder unpark |
| Paid Ads | freeze → 2026-08-06 | date + GO |
| 3D | parked | explicit unpark |
| Growth strategy gate | **not opened** | `active_gate` still null — **correct** until Founder names gate |
| SoT hygiene (this audit) | open debt | C1–C3, H1–H3 |

### NOT waiting for

- Fake S7 PASS · Mollie €2 unlock · reopening DI S4–S8 · Campus W3 as active_gate

---

## 5) Root cause of „wszystko się miesza”

```text
1) Product rename Campus → VHQ without SUPERSEDE stamp on Campus PROGRAM
2) DI sprint wrote many handoffs; I-6 archive never ran → stale "next" docs win in chat context
3) Agent tip-sync (PROGRAM-LANES) added a 3rd plan pointer without Index registration
4) brain.md / Knowledge Index links not refreshed after VHQ+DI
5) Local dirty tree (lanes + MKT) ≠ origin tip — dual reality on disk
```

**Nie** root cause: brak Order Desk SoT płatnością.

---

## 6) Protocol that should steer (no new invention)

```text
START  → /vibe-init
STEER  → todo.active_gate (null = idle / observe)
RULES  → meta global-rules + AGENTS + Knowledge Index conflict §
PROGRAM→ FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md (product) + DI scorecard (quality bar)
OPS DAY→ OPERATOR-TODAY (marketing) · JADZIA-OPERATOR-PLAYBOOK (ops)
PROOF  → handoffs (ephemeral) → archive when >15
SHIP   → /jadzia-test → /post-coding → GO DEPLOY → /jadzia-deploy
```

`PROGRAM-LANES-SOT.md` = **summary aid only** until Dowódca GO to keep or demote.

---

## 7) Recommended single next path (no-ask)

**Gate name (when Founder GO):** `VF-SOT-HYGIENE-00` (docs-only, `runtime_changes_allowed=false`)

Scope 1-1-1:
1. Stamp `FLEXGRAFIK-CAMPUS-PROGRAM.md` → `[SUPERSEDED]` by VHQ (keep as foundation pointer).  
2. Demote `PROGRAM-LANES` from `todo.plan`/`active_plan` → appendix under VHQ-PROGRAM or archive; restore plan → `FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` + scorecard pointer.  
3. Tip-sync VHQ-PROGRAM frontmatter → `0264f5d` / `2623ae2` / `vhq-w65a`.  
4. Archive cold handoffs to restore I-6 (≤15 LIVE).  
5. Refresh `brain.md` § Source of Truth (VHQ + DI + Index).  
6. Commit **without** staging `docs/ops/marketing/MKT/**`.

**Until that GO:** agent = observe. No Growth feature. No S7. No deploy.

---

## 8) Files touched by lanes rewire (uncommitted at audit)

- `todo.json`, `.cursor/current-task.md`
- `docs/ops/PROGRAM-LANES-SOT.md` (new)
- `docs/ops/marketing/OPERATOR-TODAY.md`
- `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md`
- `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` (partial)
- `docs/handoffs/2026-07-31-PROGRAM-LANES-SOT-CLOSE.md`

Treat as **pending Founder accept/reject**, not silently LIVE.
