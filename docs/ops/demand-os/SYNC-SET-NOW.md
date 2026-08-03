---
status: ACTIVE
updated: "2026-08-03"
---

# Set-now sync (safe)

SoT script: [`tools/demand_os_sync_set_now.sh`](../../../tools/demand_os_sync_set_now.sh)

## Rules

1. **Default = dry-run** (`rsync -n`)
2. **`--delete` DISABLED** (refused by script)
3. **Runtime excluded:** `LEDGER.csv`, `MEMORY.json`, `*.jsonl`, `ENGAGE-LOG*`, `CONTROL-AUDIT*`, `VALIDATOR-LOG.csv`
4. Apply only with GO deploy / explicit ops intent: `--apply`

## Commands

```bash
# dry-run
bash tools/demand_os_sync_set_now.sh jadzia@HOST:/opt/jadzia/data/demand-os/set-now

# write (no wipe)
bash tools/demand_os_sync_set_now.sh --apply jadzia@HOST:/opt/jadzia/data/demand-os/set-now
```

Phase0 markdown missing on VPS may be filled by this sync from `data/demand-os/set-now-sanitized/`.
