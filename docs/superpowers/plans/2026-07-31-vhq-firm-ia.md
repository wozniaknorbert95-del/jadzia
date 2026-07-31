# VF-VHQ-FIRM-IA-00 Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make Virtual HQ feel like one company in one home — Firm Chain IA + Console demoted from Esc parent — without building Order Desk or touching DI logic.

**Architecture:** Keep floor IDs `P0–P3`. Add parallel `firmStage` on `VHQ_ROOMS`. Fix Esc ladder so HQ never dumps to Operations Console. Always-on Firm Chain strip. PARKED rooms get `firmRole` + `unlockHint`. Cache bump `vhq-w66a`. Docs tip sync last.

**Tech Stack:** Vanilla JS Commander UI (`commander-ui/`), CSS, service worker cache string, pytest string-contract tests, SQLite untouched.

**Spec:** [`docs/superpowers/specs/2026-07-31-vhq-firm-ia-design.md`](../specs/2026-07-31-vhq-firm-ia-design.md) — **APPROVED**

## Global Constraints

- Priority: A (DI) maintain · B firm IA · C Order Desk **out of scope**
- Preserve EV-W2-010 Order Desk PARKED — no fake LIVE / no invented KPIs
- No new backend APIs · no 6th tab · no 3D · no Ads · no Mollie
- Deploy only with explicit Founder `GO DEPLOY`
- Do not stage `docs/ops/marketing/MKT/**`
- Internal chrome copy may be PL; do not invent NL customer copy
- Cache asset id for this gate: **`vhq-w66a`**

## File map

| File | Responsibility |
|------|----------------|
| `commander-ui/app.js` | `vhqEscLadder`, `vhqClose`, `VHQ_ROOMS` (+`firmStage`/`firmRole`/`unlockHint`), Firm Chain JS, room render hooks |
| `commander-ui/index.html` | CTA labels, hint, eyebrow, Firm Chain markup, floor band titles, `?v=` |
| `commander-ui/styles.css` | Firm Chain strip + stage highlight |
| `commander-ui/sw.js` | `CACHE = coi-commander-shell-vhq-w66a` |
| `tests/unit/test_vhq_firm_ia_contracts.py` | String contracts for Esc/Console/firmStage/EV-W2-010 |
| `todo.json` + ops tips | `active_gate`, tip, agent_rule for gate |
| `docs/handoffs/2026-07-31-VF-VHQ-FIRM-IA-00-BLAST.md` | BLAST before code (Task 0) |
| `docs/handoffs/2026-07-31-VF-VHQ-FIRM-IA-00-CLOSE.md` | CLOSE after dogfood |

---

### Task 0: BLAST + todo gate

**Files:**
- Create: `docs/handoffs/2026-07-31-VF-VHQ-FIRM-IA-00-BLAST.md`
- Modify: `todo.json` (header + `gate_machine`)
- Modify: `.cursor/current-task.md`

- [ ] **Step 1: Write BLAST** (binary DoD from spec §2 + §6; STOP list; WP-A→B→C)

- [ ] **Step 2: Set control plane**

```json
"active_gate": "VF-VHQ-FIRM-IA-00",
"runtime_changes_allowed": true,
"next_agent": "Implement FIRM-IA plan WP-A then WP-B. No Order Desk LIVE. No DI reopen.",
"agent_rule": "1-1-1 VF-VHQ-FIRM-IA-00. Spec docs/superpowers/specs/2026-07-31-vhq-firm-ia-design.md. Preserve EV-W2-010. Esc must not parent to Console. Deploy only with GO DEPLOY."
```

Also set `gate_machine.active` = `"VF-VHQ-FIRM-IA-00"` and `active_state` = `"firm_ia_in_progress"`.

- [ ] **Step 3: Commit**

```bash
git add docs/handoffs/2026-07-31-VF-VHQ-FIRM-IA-00-BLAST.md todo.json .cursor/current-task.md
git commit -m "docs(vhq): BLAST VF-VHQ-FIRM-IA-00 firm IA + single shell"
```

---

### Task 1: Contract tests (fail first)

**Files:**
- Create: `tests/unit/test_vhq_firm_ia_contracts.py`

**Interfaces:**
- Consumes: file text of `commander-ui/app.js`, `commander-ui/index.html`
- Produces: pytest failures until WP-A/B land

- [ ] **Step 1: Write failing tests**

```python
"""VF-VHQ-FIRM-IA-00 UI string contracts (no browser)."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
APP = (ROOT / "commander-ui" / "app.js").read_text(encoding="utf-8")
HTML = (ROOT / "commander-ui" / "index.html").read_text(encoding="utf-8")


def test_esc_ladder_does_not_parent_to_console():
    # After fix: vhqEscLadder must not call vhqGoConsole when on MC
    assert "vhqGoConsole({ focusAuth: false, historyMode: \"push\" });" not in _esc_ladder_body()
    assert "stay in HQ" in APP or "Esc ladder ends at Mission Control" in APP


def _esc_ladder_body() -> str:
    start = APP.index("function vhqEscLadder()")
    end = APP.index("\nfunction ", start + 1)
    return APP[start:end]


def test_hint_does_not_send_esc_to_console():
    assert "Esc: room → Mission Control → Operations Console" not in HTML
    assert "Operations Console" not in HTML.split("vhq-shell__hint")[1][:200]


def test_tools_cta_not_operations_console_label():
    # #vhq-to-console button text
    assert ">Operations Console</button>" not in HTML or "Tools" in HTML
    assert "Tools / Sign in" in HTML or "Narzędzia / Logowanie" in HTML


def test_firm_stage_on_core_rooms():
    for room_id, stage in [
        ("marketing-studio", "demand"),
        ("sales-room", "sell"),
        ("wizard-quote", "sell"),
        ("order-desk", "deliver"),
        ("mission-control", "direct"),
    ]:
        assert f'"{room_id}"' in APP
        # room block contains firmStage
        idx = APP.index(f'"{room_id}":')
        chunk = APP[idx : idx + 800]
        assert f'firmStage: "{stage}"' in chunk


def test_order_desk_still_parked_ev_w2_010():
    idx = APP.index('"order-desk":')
    chunk = APP[idx : idx + 1200]
    assert 'status: "PARKED"' in chunk
    assert "EV-W2-010" in chunk
    assert "unlockHint" in chunk
```

Adjust assertions in Step 1 to match the exact comment/string you will add in Task 2–3 (keep one stable comment in `vhqEscLadder`: `// Esc ladder ends at Mission Control (HQ home)`).

- [ ] **Step 2: Run — expect FAIL**

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py -v
```

Expected: FAIL on Esc/Console/firmStage assertions.

- [ ] **Step 3: Commit tests**

```bash
git add tests/unit/test_vhq_firm_ia_contracts.py
git commit -m "test(vhq): FIRM-IA contract tests (failing red)"
```

---

### Task 2: WP-A — Shell primacy (Esc + Console demotion)

**Files:**
- Modify: `commander-ui/app.js` (`vhqEscLadder` ~3888–3907, `vhqClose` ~3858–3862, click handlers ~4032–4035)
- Modify: `commander-ui/index.html` (header actions ~76–93, hint ~318)

**Interfaces:**
- Consumes: existing `vhqGoMissionControl`, `vhqGoConsole`, `vhqIsPrimary`
- Produces: Esc ends at MC; Console only via Tools CTA

- [ ] **Step 1: Fix `vhqEscLadder`**

Replace the final `vhqGoConsole(...)` branch with no-op stay on HQ (optional: ensure MC command mode):

```javascript
function vhqEscLadder() {
  if (!vhqIsPrimary()) {
    vhqClose();
    return;
  }
  // Esc ladder ends at Mission Control (HQ home) — Console is Tools only, not parent
  const onHq = document.getElementById("view-hq") && !document.getElementById("view-hq").hidden;
  if (!onHq || !vhqOpen) {
    return;
  }
  if (vhqCurrentRoom && vhqCurrentRoom !== "mission-control") {
    vhqGoMissionControl({ historyMode: "push" });
    return;
  }
  if (document.body.classList.contains("vhq-mode-world")) {
    vhqGoMissionControl({ historyMode: "push" });
    return;
  }
  // Already on MC command view — do not open Console
  return;
}
```

- [ ] **Step 2: Fix primary `vhqClose`**

When `vhqIsPrimary()`, Close must **not** call `vhqGoConsole`. Prefer go MC (or no-op if already MC):

```javascript
function vhqClose(opts = {}) {
  if (vhqIsPrimary()) {
    // Close / dismiss stays in HQ — use Tools CTA for Console
    vhqGoMissionControl({ historyMode: opts.historyMode || "push" });
    return;
  }
  // ... existing legacy branch unchanged ...
}
```

- [ ] **Step 3: Update HTML chrome**

In `index.html`:

```html
<p class="vhq-shell__eyebrow">Virtual HQ · FlexGrafik</p>
...
<button type="button" id="vhq-to-console" class="secondary">Tools / Sign in</button>
...
<!-- Remove or retarget #vhq-close: if kept, aria-label="Back to Mission Control" -->
<button type="button" id="vhq-close" class="secondary" aria-label="Back to Mission Control">Close</button>
...
<p class="vhq-shell__hint hint">Esc: room → Mission Control · Tools / Sign in for JWT · No 3D · Cache vhq-w66a</p>
```

(Keep cache string update for Task 5 if you prefer single bump — then leave `vhq-w65a` until Task 5.)

- [ ] **Step 4: Run contract tests for Esc/hint/CTA**

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py -v
```

Expected: Esc/hint/CTA tests PASS; firmStage tests still FAIL.

- [ ] **Step 5: Manual smoke (local static)**

Serve `commander-ui` (or existing local URL). Cold open HQ → open Sales room → Esc → MC → Esc again → **still HQ**. Click Tools / Sign in → Console → Return to HQ.

- [ ] **Step 6: Commit**

```bash
git add commander-ui/app.js commander-ui/index.html
git commit -m "fix(vhq): FIRM-IA Esc ends at HQ; Console is Tools only"
```

---

### Task 3: WP-B — `firmStage` + unlock copy on rooms

**Files:**
- Modify: `commander-ui/app.js` (`VHQ_ROOMS` manifest)

**Interfaces:**
- Produces: every floorCard room has `firmStage`; PARKED deliver rooms have `firmRole` + `unlockHint`

- [ ] **Step 1: Add fields (canonical map)**

| room id | firmStage |
|---------|-----------|
| `marketing-studio` | `demand` |
| `sales-room`, `wizard-quote`, `design-studio`, `client-support` | `sell` |
| `order-desk`, `production-control`, `preflight-quality`, `dispatch-returns`, `supplier-dock`, `partner-production-network`, `asset-warehouse` | `deliver` |
| `mission-control`, `approval-vault`, `ai-agent-health`, `boardroom`, `analytics-finance`, `compliance-audit`, `knowledge-library`, `data-ai-lab`, `vcms-os-zone`, `design-agent-probe` | `direct` |

Example for Order Desk:

```javascript
"order-desk": {
  // ...existing fields...
  firmStage: "deliver",
  firmRole: "Tu firma domyka zamówienie i produkcję — dziś bez biurka SoT.",
  unlockHint: "Wymaga Order Desk SoT + unpark EV-W2-010 (osobny projekt). INT-002 ≠ desk.",
  status: "PARKED",
  evidence: "EV-W2-010",
  // keep action: null
},
```

Add the same pattern for other PARKED/PLANNED deliver rooms (role + unlockHint). For LIVE/PARTIAL rooms, `firmRole` one-liner is enough; `unlockHint` optional.

- [ ] **Step 2: Render role/unlock in room Work View**

In `vhqRenderRoom` honesty/header block (~2578 / ~3241), after status badge, if `room.firmRole` or `room.unlockHint`:

```javascript
if (room.firmRole) {
  root.appendChild(vhqEl("p", "vhq-firm-role", room.firmRole));
}
if (room.unlockHint) {
  root.appendChild(vhqEl("p", "hint vhq-unlock-hint", room.unlockHint));
}
```

(Use existing `vhqEl` helper; place near honesty banners.)

- [ ] **Step 3: Run firmStage contract tests**

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py -v
```

Expected: `test_firm_stage_on_core_rooms` + order desk unlock PASS (after strip HTML still optional).

- [ ] **Step 4: Commit**

```bash
git add commander-ui/app.js
git commit -m "feat(vhq): firmStage + PARKED role/unlock copy on VHQ rooms"
```

---

### Task 4: WP-B — Firm Chain strip + floor band labels

**Files:**
- Modify: `commander-ui/index.html` (insert strip above floor tabs ~98)
- Modify: `commander-ui/styles.css`
- Modify: `commander-ui/app.js` (bind strip + highlight)

**Interfaces:**
- Consumes: `room.firmStage`
- Produces: `#vhq-firm-chain` always visible

- [ ] **Step 1: HTML strip + relabel floors**

```html
<nav id="vhq-firm-chain" class="vhq-firm-chain" aria-label="Firm value chain">
  <button type="button" class="vhq-firm-stage" data-firm-stage="demand">1 Popyt</button>
  <button type="button" class="vhq-firm-stage" data-firm-stage="sell">2 Sprzedaż</button>
  <button type="button" class="vhq-firm-stage" data-firm-stage="deliver">3 Realizacja</button>
  <button type="button" class="vhq-firm-stage" data-firm-stage="direct">4 Sterowanie</button>
</nav>
<!-- existing floor tabs keep data-floor P3..P0 -->
<button ... data-floor="P3">P3 Sterowanie</button>
<button ... data-floor="P2">P2 Wiedza / ryzyko</button>
<button ... data-floor="P1">P1 Popyt / sprzedaż</button>
<button ... data-floor="P0">P0 Realizacja</button>
```

Update band titles similarly (`P3 — Sterowanie`, etc.).

- [ ] **Step 2: CSS (minimal, match existing VHQ tokens)**

```css
.vhq-firm-chain {
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem;
  padding: 0.35rem 0.75rem;
}
.vhq-firm-stage {
  /* reuse secondary button look; active = aria-current / .is-active */
}
.vhq-firm-stage.is-active {
  font-weight: 700;
}
.vhq-room-card[data-firm-stage].is-dim {
  opacity: 0.45;
}
```

- [ ] **Step 3: JS bind**

```javascript
const VHQ_FIRM_STAGES = ["demand", "sell", "deliver", "direct"];

function vhqSetFirmStageFilter(stage) {
  document.querySelectorAll(".vhq-firm-stage").forEach((btn) => {
    btn.classList.toggle("is-active", btn.dataset.firmStage === stage);
    btn.setAttribute("aria-current", btn.dataset.firmStage === stage ? "true" : "false");
  });
  document.querySelectorAll(".vhq-room-card[data-firm-stage]").forEach((card) => {
    const match = !stage || card.dataset.firmStage === stage;
    card.classList.toggle("is-dim", stage && !match);
  });
}

function vhqBindFirmChain() {
  document.querySelectorAll(".vhq-firm-stage").forEach((btn) => {
    btn.addEventListener("click", () => {
      const stage = btn.dataset.firmStage;
      const already = btn.classList.contains("is-active");
      vhqSetFirmStageFilter(already ? null : stage);
    });
  });
}
```

When rendering floor cards, set `data-firm-stage={room.firmStage}`. On room open, call `vhqSetFirmStageFilter(room.firmStage)` to sync strip (do not clear floor tab).

Call `vhqBindFirmChain()` from existing VHQ init (near floor tab bind).

- [ ] **Step 4: Manual smoke**

Strip visible on P3 and after switching to P0. Click Realizacja → Order Desk card not dimmed; Marketing dimmed. Clear filter by second click.

- [ ] **Step 5: Commit**

```bash
git add commander-ui/index.html commander-ui/styles.css commander-ui/app.js
git commit -m "feat(vhq): Firm Chain strip + firm-aligned floor labels"
```

---

### Task 5: Cache bump `vhq-w66a`

**Files:**
- Modify: `commander-ui/index.html` (`styles.css?v=`, `app.js?v=`, hint cache text)
- Modify: `commander-ui/sw.js` (`CACHE` constant)

- [ ] **Step 1: Replace `vhq-w65a` → `vhq-w66a` in those three places**

- [ ] **Step 2: Commit**

```bash
git add commander-ui/index.html commander-ui/sw.js
git commit -m "chore(vhq): cache bump vhq-w66a for FIRM-IA"
```

---

### Task 6: WP-C — full pytest + local dogfood + tip docs

**Files:**
- Modify: `todo.json`, `docs/ops/PROGRAM-LANES-SOT.md`, `docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md` (tip/cache only)
- Create: `docs/handoffs/2026-07-31-VF-VHQ-FIRM-IA-00-CLOSE.md` (after dogfood)
- Optional PRECLOSE notes in handoff

- [ ] **Step 1: Run contracts + DI regression slice**

```bash
pytest tests/unit/test_vhq_firm_ia_contracts.py tests/unit/test_commander_money_narrative.py tests/unit/test_commander_nba.py -v
```

Expected: all PASS; money narrative still mentions EV-W2-010.

- [ ] **Step 2: Local dogfood checklist (record in CLOSE)**

1. Cold open HQ/MC  
2. Esc room→MC; second Esc stays HQ  
3. Tools / Sign in → Console → Return to HQ  
4. Firm Chain visible; stages dim correctly  
5. Order Desk PARKED + role + unlock; no euro KPI  
6. NBA + money-risk + Vault still on MC  

- [ ] **Step 3: Tip sync + CLOSE handoff + todo `active_gate: null` after CLOSE** (or keep gate until deploy GO — prefer: `active_gate` stays until deploy CLOSE)

- [ ] **Step 4: Commit docs**

```bash
git add todo.json docs/ops/PROGRAM-LANES-SOT.md docs/ops/FLEXGRAFIK-VIRTUAL-HQ-PROGRAM.md docs/handoffs/2026-07-31-VF-VHQ-FIRM-IA-00-CLOSE.md
git commit -m "docs(vhq): PRECLOSE/CLOSE notes VF-VHQ-FIRM-IA-00 local dogfood"
```

- [ ] **Step 5: Push**

```bash
git push origin HEAD
```

- [ ] **Step 6: Stop for Founder** — emit deploy pack; **do not deploy** until `GO DEPLOY VF-VHQ-FIRM-IA-00`

---

### Task 7: Deploy + prod dogfood (human GO only)

**Files:**
- Create: `docs/handoffs/2026-07-31-DEPLOY-VHQ-FIRM-IA-00-CLOSE.md`
- Modify: `todo.json` tip sync to docs tip after deploy

- [ ] **Step 1: Wait for explicit GO**

- [ ] **Step 2: Run `/jadzia-deploy` workflow** (VPS pull/restart per playbook)

- [ ] **Step 3: Prod dogfood** `?v=vhq-w66a` — same checklist as Task 6

- [ ] **Step 4: CLOSE deploy + set `active_gate: null`, `active_state: sot_hygiene_done_idle` or `firm_ia_done_idle`**

---

## Spec coverage check

| Spec requirement | Task |
|------------------|------|
| Esc not parent to Console | Task 2 |
| Tools / Sign in CTA | Task 2 |
| Hint update | Task 2 |
| Eyebrow firm framing | Task 2 |
| firmStage axis | Task 3 |
| PARKED role + unlock | Task 3 |
| Firm Chain strip | Task 4 |
| Floor relabel (keep P* ids) | Task 4 |
| Cache bump | Task 5 |
| DI / EV-W2-010 regression | Task 1 + 6 |
| No Order Desk LIVE | STOP + tests Task 1 |
| Docs / todo gate | Task 0 + 6 + 7 |

## Placeholder scan

None intentional. CTA language locked to `Tools / Sign in` (EN chrome OK for this gate; PL alternate allowed if already dominant in header — pick one and keep tests in sync).
