# Handoff — CMD-DASH-COMPLETE-01 Wave A (DS-0 + Marketing Decision Rail)

**Date:** 2026-07-22  
**Branch:** `feat/cmd-dash-complete-wave-a`  
**Cache:** `mkt-dash04`  
**standing_go_closeout:** `false` (session GO for deploy if Wave A 100% + CI green)

## DONE

| Item | Stan |
|------|------|
| DS-0 CSS | `sev-chip` / `exec-rail` / `decision-card` / `forensic-panel` / `kpi-tile` + nav `aria-current` underline |
| PARKS-LIVE | Static H-Meta parks HTML **removed** |
| MB-PANEL | L0 Decision Rail: preflight · breakers · accuracy · FB · held · memory |
| Forensic L2 | shadow last-N · brain-bus events/flags · memory (collapsed `<details>`) |
| Hard STOP | **0** `actions/execute` in UI · **5** primary tabs (D0.15) · Audyt secondary only |
| Tests | `tests/unit/test_commander_wave_a_ui.py` + MB preflight/breakers PASS |
| Verify script | greps `mkt-dash04` + rail APIs |

## LEFT

- Merge PR → deploy VPS (session GO when CI green) → phone dogfood Marketing L0  
- **Wave B:** Home ops chip-rail + `CMD-DASH-AGENTS-TRUTH-01`  
- Wave C/D per plan

## DoD Wave A

- [x] Marketing L0 rail wired (JWT soft-fail)  
- [x] Static parks gone  
- [ ] Prod tip LIVE + dogfood ≤3s after auth  

## Start next

```text
@vibe-init
TASK_ID: CMD-DASH-COMPLETE-01
Cel: Wave B — Home ops chip-rail + Agenci truth (next_expected_run + AI OS map).
Hard STOP: no execute UI, no 6th Audyt tab, standing_go_closeout=false.
Read: docs/handoffs/2026-07-22-CMD-DASH-COMPLETE-01-WAVE-A-HANDOFF.md
```
