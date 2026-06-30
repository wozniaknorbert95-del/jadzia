---
status: COMPLETED
archived: 2026-06-30
---

# Stage 2 Verification — jadzia-core

**Date:** 2026-05-23  
**Status:** DONE  
**Repo:** jadzia-core (AI backend / FastAPI / LangGraph)

## Artifact counts

| Item | Count |
|------|-------|
| `.cursor/skills/` (6 CORE + 3 repo-specific) | 9 |
| `.agents/workflows/` | 10 (incl. pre-flight) |
| `.opencode/agents/` | 1 (`jadzia-builder`) |

## Cursor skills inventory

| Skill | Type | Workflow 1:1 |
|-------|------|--------------|
| vibe-init | CORE | yes |
| blast | CORE | yes |
| debug | CORE | yes |
| audit-red-team | CORE | yes |
| handoff | CORE | yes |
| context-reset | CORE | yes |
| jadzia-migrate | repo-specific | yes |
| jadzia-test | repo-specific | yes |
| jadzia-deploy | repo-specific | yes |

## CORE pipeline alignment

| Check | Status |
|-------|--------|
| Feature → `/blast` | yes |
| Bugfix unknown → `/debug` | yes |
| Schema → `/jadzia-migrate` | yes |
| Deploy path → test → audit → jadzia-deploy | yes |
| Output `CURRENT_STAGE` + `RECOMMENDED_NEXT` | yes |
| Zasada 11 AWAIT_COMMANDER on deploy | yes |
| jadzia-core.mdc lists CORE index | yes |

## Weakness matrix (portal parity)

Controls 1–5, 7–10 covered via CORE skills; control 6 via `/jadzia-test` + pytest CI.

## OpenCode

- `jadzia-builder.yaml` — F1–F6 routing, VPS deploy prep only
- `agents.yaml` — default_agent: jadzia-builder, deploy_policy autonomous: false

## Next

**app.flexgrafik.nl** S2-APP-01 per WorkFlow/todo.json.
