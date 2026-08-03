---
status: READY
updated: "2026-08-03"
item: 4-TOOL-02
mode: test→delete only
---

# 4-TOOL-02 — Tool-proof publish path (test→delete)

Engineering proof only. **Never** advances live P0 SEAL.

## Path

1. Confirm gate ALLOW (dry):  
   `python tools/demand_os_f2.py gate --asset-id tt_w32_install_01`
2. Prefer **dry** path via publish gate bridge (`dry_run=True`).
3. If a real test upload is required for transport proof:
   - publish as test
   - **delete** immediately
   - LEDGER notes: `TEST · deleted · 4-TOOL-02` · `publish_Y/N=N`
4. Do not set calendar status to `published` for live SEAL.
5. Keep `4-P0-*` `blocked`.

## Ledger template (test only)

```csv
2026-08-03,tiktok,installateur,tt_w32_install_01,<utm>,N,0,0,0,0,4-TOOL-02 TEST · deleted · not live P0
```

## STOP

- `publish=Y` as live evidence
- Founder cadence / Ads / boost
- Closing `4-P0-01` from this path
