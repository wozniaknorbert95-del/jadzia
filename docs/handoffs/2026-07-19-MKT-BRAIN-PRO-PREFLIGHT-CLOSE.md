# Handoff — MKT-BRAIN-PRO-PREFLIGHT CLOSE

**Date:** 2026-07-19  
**Gate:** MKT-BRAIN-PRO (#2 shadow → GO propose)  
**Status:** PREFLIGHT PASS · `MB_MODE` nadal `shadow` · F4 BLOCKED

## Roadmapa (nietykalna kolejność)

| # | Co | Stan |
|---|-----|------|
| 1 | META lean | HOLD published €5 |
| 2 | Eval → GO propose | gate PASS + preflight READY_FOR_GO |
| 3 | Purchase | PARK |
| 4 | F4 Act | blocked do GO |
| 5 | FB read_insights | open |

## Deliverables

- `agent/marketing/propose_preflight.py`
- `scripts/mb_propose_preflight.py`
- `GET /api/v1/commander/marketing/propose-preflight`
- `docs/ops/marketing/PROPOSE-CUTOVER.md`
- `tests/unit/test_mb_propose_preflight.py` — **5/5 PASS**

## VPS evidence (read-only, tip `ab1ed04`)

```
mb_mode shadow
accuracy 1.0 n 20 gate True
breakers ['CB_SHADOW']
data_health amber
eco_red 0
memory chroma 20
verdict READY_FOR_GO
ticket GO propose — accuracy=100% n=20 — tip=ab1ed04 — preflight=READY_FOR_GO
```

## Human next (HITL)

1. Ticket: `GO propose — accuracy=100% n=20 — tip=ab1ed04 — preflight=READY_FOR_GO`
2. Po GO: deploy tip z PREFLIGHT + ręczny flip `MB_MODE=propose` — [PROPOSE-CUTOVER.md](../ops/marketing/PROPOSE-CUTOVER.md)
3. Meta #1: hold 7d; WA &lt;15 min na lead

## Agent next

- **NIE** flip `propose` bez GO
- Po GO deploy: verify preflight endpoint LIVE + breakers bez `CB_SHADOW` w propose
- F4 Act dopiero po propose + governance path
