---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO F2b + Wave B eval — CLOSE"
gate: "MKT-BRAIN-PRO-F2b"
updated: "2026-07-19"
result: "PASS LIVE tip 3c4af26 — memory + eval-pack; F4/propose BLOCKED"
---

# MKT-BRAIN-PRO F2b + Shadow Eval Ops — CLOSE

## VPS evidence

| Check | Result |
|-------|--------|
| tip | **`3c4af26`** |
| health | OK |
| memory_source | **chroma** · synced 7 · cycle `memory=['chroma']` |
| eval-pack | rubric True · count≥5 |
| MB_MODE | **shadow** (unchanged) |

## Wave A — Campaign Memory

| Item | Status |
|------|--------|
| `agent/marketing/campaign_memory.py` | DONE (hash embed + Chroma + SQL degrade) |
| Wire `decision_engine` / `runtime` sync | DONE |
| `GET …/marketing/memory/status` + `POST …/sync` | DONE |
| pytest `test_mb_f2b_memory.py` | PASS |

## Wave B — Shadow Evaluation Ops

| Item | Status |
|------|--------|
| `agent/marketing/shadow_eval.py` + rubric ≥70% | DONE |
| `GET …/marketing/shadow/eval-pack` | DONE |
| `scripts/mb_shadow_eval_export.py` | DONE |
| STATUS BOARD rubric + F4 cutover checklist | DONE |

## Wave C — F4 readiness

Checklist w `MKT-BRAIN-PRO.md` STATUS BOARD. **`MB_MODE` remains `shadow`.** No Act.

## GO propose template (human)

```
GO propose YYYY-MM-DD
accuracy=<pct>% (agree/partial/disagree counts)
tip=<sha>
Purchase=PARK|PASS
```

## PARK / STOP

Gate D · Mollie LIVE · Ads API create · `MB_MODE=propose` without GO
