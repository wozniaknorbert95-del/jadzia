# Handoff — CMD-DASH-TRUST-01 (ops health + DA health)

**Date:** 2026-07-21  
**Status:** **LIVE** @ tip **`f57dab3`** (PR #11 merged + VPS deploy)  
**standing_go_closeout:** `false`

## Deploy evidence

```text
PREV=3604f60 HEAD=f57dab3 tip_ok
systemctl=active uvicorn=1
da_health_local status=ok
da_health_public 200
worker_health healthy ssh=ok
commander 200
mkt-dash03_count=2 worker_health_in_app=1
```

## Changes

1. **Home strip** (`commander-ui/app.js`): soft-fetch `GET /worker/health` → Ops/SSH/SQLite/Loop/Up + existing SLA/GA4/freshness
2. **Design Agent health** (`api/routes/design_agent.py`): public `GET /api/v1/design-agent/health`
3. Cache bust **`mkt-dash03`**
4. Verify script aligned + health probes
5. Unit test `test_design_agent_health_200`

## LEFT

- `CMD-DASH-PARKS-LIVE-01` · `CMD-DASH-MB-PANEL-01` · `CMD-DASH-AGENTS-TRUTH-01` · `CMD-DASH-ORPHAN-SOT-01`

Hard-refresh: `https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash03`
