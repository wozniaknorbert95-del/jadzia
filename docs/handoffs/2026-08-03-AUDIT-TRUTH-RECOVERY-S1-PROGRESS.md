---
status: PROGRESS · NOT CLOSE
title: "Audit Truth-Recovery — Bramka 0 + K2/K4 code advance (still partial)"
date: 2026-08-03
tip: uncommitted
cache: desk-dash09 (bump pending)
branch: master
active_item: 4-AWAIT-UNLOCK
live_publish: none
honesty: "K2=partial · K4=partial · ZERO false DONE"
---

# Progress — Audit Truth-Recovery (not sealed)

## Decision

False DONE on K2/K4 retracted. Canonical register: [`docs/ops/demand-os/AUDIT-K-REGISTER.md`](../ops/demand-os/AUDIT-K-REGISTER.md).

## Done this slice (code + tests only)

### Bramka 0
- Truthful K1–K14 register created
- Roadmap statuses corrected to `partial` / `not_started`

### K2 (partial → still partial)
- `ga4_adapter.py`: `status=unavailable` for stub/missing/error; split `ga4_sessions_7d` / `ga4_wizard_starts_7d`
- `commander_status.py`: payload exposes split fields + `utm_attributed_starts`
- UI: tile shows `niedostępne` when unavailable; tooltip says sessions ≠ starts
- Tests: `test_ga4_adapter.py`, `test_commander_status_ga4.py` green

### K4 (partial → still partial)
- `desk_copy.py` + `DESK_COPY` in UI
- Empty/error/CTA jargon removed from desk primary surface
- Copy forbid test green
- HTML: Rola / Dziennik dziś / Brak połączenia / Sesje GA4 (7d)

## Explicitly NOT done

| Claim | Reality |
|-------|---------|
| K2 done | **FALSE** — stub default; no VPS live proof |
| K4 done | **FALSE** — not committed, not cache-bumped, not deployed, no screenshots |
| Live starts in desk | **FALSE** — North Star still ledger/events; GA4 sessions only when live |
| Deployed to founder | **FALSE** — local only |

## Verify

```text
pytest tests/unit/test_ga4_adapter.py tests/unit/test_commander_status_ga4.py tests/unit/test_demand_desk_ui_contracts.py -q
→ 44 passed

DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized python tools/demand_os_owner_verify.py
→ ok: true · 113 demand-os passed
```

## Files touched (uncommitted)

- `agent/demand_os/ga4_adapter.py`
- `agent/demand_os/commander_status.py`
- `agent/demand_os/desk_copy.py` (new)
- `agent/demand_os/desk_contract.py`
- `commander-ui/app.js`
- `commander-ui/index.html`
- `tests/unit/test_ga4_adapter.py` (new)
- `tests/unit/test_commander_status_ga4.py` (new)
- `tests/unit/test_demand_desk_ui_contracts.py`
- `tests/unit/test_render_desk_golden.py`
- `tests/fixtures/desk_status_v21.min.json`
- `docs/ops/demand-os/AUDIT-K-REGISTER.md` (new)
- `.cursor/plans/audit-k-roadmap.md`
- this handoff

## RECOMMENDED_NEXT

```text
1) Commit when Dowódca asks (include cache bump desk-dash10)
2) After fresh GO: deploy + optional DEMAND_OS_GA4_LIVE=1 proof
3) Only then reassess K2/K4 for DONE against AUDIT-K-REGISTER
4) Sprint S2: K1 attribution + K3 auth — still not_started
```

Live P0 PARKED. No Founder publish push.
