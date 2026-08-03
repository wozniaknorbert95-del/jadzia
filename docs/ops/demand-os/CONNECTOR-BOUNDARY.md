---
status: ACTIVE
updated: "2026-08-03"
scope: "Demand OS tool 100% connector honesty"
---

# Connector boundary (fail-closed)

**Decision:** Tool 100% = **honest stub/registry modes**, not full live Google Drive/GA4.

| Connector | Default mode | Live flag | Tool 100% DoD |
|-----------|--------------|-----------|---------------|
| GA4 | `stub` · `ok: false` · empty starts | `DEMAND_OS_GA4_LIVE=1` | never invent UTM rows |
| GDrive CF | `local_registry` from ASSET-REGISTRY.csv | `DEMAND_OS_GDRIVE_LIVE=1` | LIVE without API → `not_wired` · `ok: false` |
| MCP facade | CLI wrappers only | n/a | no invented ledger/calendar rows |
| TT transport | stub / PARKED comments | n/a | no autonomous publish |

## Doctor

`hub doctor` requires `gdrive_local_registry` (default path).  
Does **not** require GA4 LIVE or Drive folder API.

## Verify

```bash
python -c "from agent.demand_os.ga4_adapter import fetch_wizard_starts; print(fetch_wizard_starts())"
python -c "from agent.demand_os.gdrive_cf import list_cf_assets; print(list_cf_assets(limit=2))"
```

Expected without live flags: GA4 stub fail-closed; GDrive `local_registry` ok.
