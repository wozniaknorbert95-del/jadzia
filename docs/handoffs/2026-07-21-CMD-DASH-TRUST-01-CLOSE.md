# Handoff — CMD-DASH-TRUST-01 (ops health + DA health)

**Date:** 2026-07-21  
**Branch:** `feat/cmd-dash-trust-01`  
**Tasks closed:** `CMD-DASH-OPS-HEALTH-01` · `CMD-DASH-DEAD-HOP-01` · `CMD-DASH-VERIFY-01`  
**standing_go_closeout:** `false` — deploy only with explicit GO (this session: user asked deploy)

## Changes

1. **Home strip** (`commander-ui/app.js`): soft-fetch `GET /worker/health` → Ops/SSH/SQLite/Loop/Up + existing SLA/GA4/freshness
2. **Design Agent health** (`api/routes/design_agent.py`): public `GET /api/v1/design-agent/health`
3. Cache bust **`mkt-dash03`**
4. Verify script aligned + health probes
5. Unit test `test_design_agent_health_200`

## Deploy checklist

```bash
# VPS after merge to master
cd /opt/jadzia && git pull --ff-only origin master
# static UI only needs restart if code py changed — yes restart
systemctl restart jadzia
curl -sf http://127.0.0.1:8000/api/v1/design-agent/health
curl -sf http://127.0.0.1:8000/worker/health | head
# Commander hard-refresh: ?v=mkt-dash03
```

## LEFT

- `CMD-DASH-PARKS-LIVE-01` · `CMD-DASH-MB-PANEL-01` · `CMD-DASH-AGENTS-TRUTH-01` · `CMD-DASH-ORPHAN-SOT-01`
