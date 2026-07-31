---
description: L3–L4 agentic drain of VHQ Decision Instrument scorecard (S1–S8) to 5/5 with tests + evidence.
---

# /vhq-decision-instrument

## Goal

Close Virtual HQ **Decision Instrument Scorecard** dimensions to **5/5** one gate at a time (1-1-1), with pytest/smoke, honest PASS, and prod evidence.  
SoT: `docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md`.

## When to use

- After `/vibe-init` when `todo.gate_machine.decision_instrument` is active or `closeout_queue` head is `VF-VHQ-DI-*`.
- Founder asks to “finish scorecard / 100% decision instrument”.

## Hard STOP

- Fake KPI / fake LIVE / greenwash `insufficient_data`
- Unpark Order Desk without SoT evidence (S7)
- Ads / Mollie / Gate D / secrets / OS↔jadzia merge without separate GO
- 3D before scorecard S4–S6 PASS + explicit unpark
- Mega-diff across multiple S* dimensions in one commit
- Stage `docs/ops/marketing/**`

## Procedure (one S* gate)

### 0. Anchor

```text
Read: todo.json active_gate + closeout_queue[0]
Read: docs/ops/VHQ-DECISION-INSTRUMENT-SCORECARD.md → target dimension DoD
Read: research docs/handoffs/2026-07-31-VF-VHQ-DECISION-INSTRUMENT-RESEARCH.md (if SNR/NBA)
```

If queue head ≠ active_gate → set active to head or STOP with handoff.

### 1. BLAST

- `docs/handoffs/YYYY-MM-DD-<GATE>-BLAST.md`
- Copy binary DoD rows from scorecard into BLAST
- `todo.active_gate=<GATE>`, `runtime_changes_allowed` only if code gate

### 2. Spec → tests first

| Change type | Minimum tests |
|-------------|----------------|
| Queue/severity/NBA policy | `tests/unit/test_commander_queue.py` (+ new rank tests) |
| Escalation / INFO hygiene | `tests/unit/test_commander_escalation.py` |
| Approvals L2/L3 | existing commander approval / ops_bus tests |
| UI-only chrome | smoke markers + manual dogfood checklist (no fake unit) |

Write failing test for new DoD **before** or **with** implementation; never CLOSE without green pytest for policy code.

### 3. Implement (minimal surface)

- Prefer API/policy over UI cosmetics (research SNR lesson)
- Preserve EV-W2-010 honesty
- Cache bump `vhq-wNNa` only if `commander-ui/**` changes

### 4. Validate

```bash
# scoped — expand only if imports demand
pytest tests/unit/test_commander_queue.py tests/unit/test_commander_escalation.py -q
# plus any new DI test module
```

Also run `/jadzia-test` if gate touches runtime beyond commander unit surface.

FAIL → fix or PARK with reason; **no fake PASS**.

### 5. Ship + release

- Follow `/post-coding` ship steps
- Deploy **only** with in-session `GO DEPLOY` / `GO jadzia-deploy` or `standing_go_closeout`
- Runtime change → backup SQLite + pull + restart + `/health` + worker health

### 6. Prod dogfood (mandatory for scorecard bump)

Cold-open: `https://api.zzpackage.flexgrafik.nl/commander/?v=<cache>`

Record in evidence dir:

| Metric | Required |
|--------|----------|
| Decide-now composition | titles + severities |
| Stub contamination | must be 0% if S4 |
| Ops summary | fire vs confidence |
| Timer Q3+Q6 (S5/S8) | ≤30s when claimed |
| Screenshot | ≥1 |

Update scorecard table row **only after** evidence.

### 7. CLOSE + queue tip

- CLOSE handoff
- `todo.gate_machine.<gate>=completed`
- Pop from `closeout_queue`
- Set `active_gate` to next DI gate **or** leave idle if Founder-only S7
- Tip-sync docs commit

### 8. Continue

- Next agent-capable gate → start `/vhq-decision-instrument` again (or Automation)
- S7 `blocked_sot` → `ready_for_human` checklist (Order SoT), zero A/B questions

## Output

```text
DI_GATE: VF-VHQ-DI-S…
SCORE_DIM: S4|S5|…
DOD: PASS|FAIL|BLOCKED_SOT
PYTEST: N/N
TIP: …
CACHE: vhq-…
EVIDENCE: docs/handoffs/evidence-…
NEXT: <next gate> | ready_for_human | CLOSEOUT_DONE

---
CURRENT_STAGE: L3-DI / L3.5 / L4
RECOMMENDED_NEXT: /vhq-decision-instrument | /post-coding | /handoff
---
```

## Mapping queue (canonical)

1. `VF-VHQ-DI-S4-SNR-FINISH` — analytics_stale / noise &lt;10%  
2. `VF-VHQ-DI-S5-NBA` — ranked next action  
3. `VF-VHQ-DI-S6-MONEY` — money/risk narrative  
4. `VF-VHQ-DI-S3-APPROVAL` — L2 honesty maturity → 5  
5. `VF-VHQ-DI-S8-VERIFY` — composite ≤30s dogfood  
6. `VF-VHQ-DI-S7-LOOP` — blocked until Order SoT GO  

S1/S2 = regression checks inside every gate dogfood (not separate unlock).
