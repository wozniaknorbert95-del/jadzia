---
status: "[ACTIVE · SET NOW PACK]"
title: "Demand OS — SET NOW artifacts (Phase 0)"
updated: "2026-07-31"
gate: "DEMAND-OS-SET-NOW-00"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md §C"
---

# SET NOW Pack — Phase 0

Artefakty ustawień przed kodem. Agent uzupełnia pliki; Dowódca robi tylko fizyczny TT/FB po `2026-08-02`.

| Plik | TODO | OS |
|------|------|-----|
| [`ICP-WEEK.md`](./ICP-WEEK.md) | DOS-C1-01 | C.1 #1 |
| [`PRIMARY-CHANNEL.md`](./PRIMARY-CHANNEL.md) | DOS-C1-02 | C.1 #2 |
| [`UTM-TEMPLATE.md`](./UTM-TEMPLATE.md) | DOS-C1-03 · C1-04 | C.1 #3–4 |
| [`ADS-FREEZE.md`](./ADS-FREEZE.md) | DOS-C1-05 | C.1 #5 |
| [`STL-CHECKLIST.md`](./STL-CHECKLIST.md) | DOS-C1-06 | C.1 #6 |
| [`DA-WIZARD-NL.md`](./DA-WIZARD-NL.md) | DOS-C1-07 | C.1 #7 · B.7 |
| [`MONEY-CHECK.md`](./MONEY-CHECK.md) | DOS-C1-08 · W1-01 | C.1 #8 · K |
| [`MONEY-CHECK-OPS.md`](./MONEY-CHECK-OPS.md) | DOS-W1-01 | Agent_Growth_Lead |
| [`MONEY-CHECK-LOG.csv`](./MONEY-CHECK-LOG.csv) | DOS-W1-01 | Agent_Growth_Lead |
| [`FB-ALLOWLIST.md`](./FB-ALLOWLIST.md) | DOS-C2-01 | C.2 |
| [`TT-ENGAGE.md`](./TT-ENGAGE.md) | DOS-C3-01 | C.3 |
| [`BLOG-ICP-W1.md`](./BLOG-ICP-W1.md) | DOS-C4-01 | C.4 |
| [`VALIDATOR-CHECKLIST.md`](./VALIDATOR-CHECKLIST.md) | DOS-C5-01 | C.5 |
| [`WAVE1-ROSTER.md`](./WAVE1-ROSTER.md) | DOS-C6-01 | C.6 |
| [`LEDGER.csv`](./LEDGER.csv) | DOS-C7-01 | C.7 |
| [`ICP-BRIEF-W1.md`](./ICP-BRIEF-W1.md) | DOS-W1-02 | B.3 |
| [`TT-SHOOT-PLAN-W1.md`](./TT-SHOOT-PLAN-W1.md) | DOS-W1-03 prep | Agent_TT |
| [`VALIDATOR-LOG.csv`](./VALIDATOR-LOG.csv) | DOS-W1-05 | Sniper_Validator |
| [`VALIDATOR-DRILL-W1.md`](./VALIDATOR-DRILL-W1.md) | DOS-W1-05 | Sniper_Validator |

**Verify:** `python tools/demand_os_phase0_check.py`  
**Runner:** `/demand-os-execute` · state: [`../STATE.md`](../STATE.md) · **next human:** `DOS-W1-03` ≥2026-08-02 · **deploy:** STOP (docs)
