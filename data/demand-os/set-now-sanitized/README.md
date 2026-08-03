---
status: "[SANITIZED PACK · OPS HARDENING]"
title: "Demand OS — set-now-sanitized"
updated: "2026-08-03"
---

# SET NOW — sanitized pack

Source for safe sync → VPS `data/demand-os/set-now` via [`SYNC-SET-NOW.md`](../../../docs/ops/demand-os/SYNC-SET-NOW.md).

## REQUIRED (phase0 doctor)

| File | Role |
|------|------|
| `README.md` | this index |
| `ICP-WEEK.md` | ICP week |
| `PRIMARY-CHANNEL.md` | channel SoT |
| `UTM-TEMPLATE.md` | UTM lock |
| `ADS-FREEZE.md` | Ads parked_cash |
| `STL-CHECKLIST.md` | STL |
| `DA-WIZARD-NL.md` | DA copy |
| `MONEY-CHECK.md` | money check |
| `FB-ALLOWLIST.md` | hunt allowlist |
| `TT-ENGAGE.md` | TT engage rules |
| `BLOG-ICP-W1.md` | blog ICP |
| `VALIDATOR-CHECKLIST.md` | Val rules |
| `WAVE1-ROSTER.md` | wave1 roles |
| `ICP-BRIEF-W1.md` | ICP brief |
| `LEDGER.csv` | ledger (**not overwritten by sync**) |

## OPTIONAL / ops (may live only in docs set-now)

| File | Note |
|------|------|
| `GO-DAY-TODAY.md` | tip |
| `VALIDATOR-LOG.csv` | runtime — sync excludes |
| `A2A-HANDOFFS.jsonl` | runtime — sync excludes |
| `MEMORY.json` | runtime — sync excludes · prefer `DEMAND_OS_MEMORY` |
| captions / ASSET-REGISTRY | usually docs pack |

## Sync rules

- dry-run default · no `--delete`
- excludes: LEDGER, MEMORY, `*.jsonl`, ENGAGE-LOG, VALIDATOR-LOG

## Verify

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_phase0_check.py
python tools/demand_os_hub.py doctor
python tools/demand_os_owner_verify.py
```
