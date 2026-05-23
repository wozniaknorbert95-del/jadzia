# HANDOFF — jadzia-core Stage 2 — 2026-05-23

## DONE

- **S2-JAD-01** — 6 CORE skills + 3 repo-specific (`jadzia-migrate`, `jadzia-test`, `jadzia-deploy`)
- Workflows 1:1 in `.agents/workflows/` (10 files incl. pre-flight)
- OpenCode `jadzia-builder` + `agents.yaml` (deploy_policy autonomous: false)
- Updated `.cursor/rules/jadzia-core.mdc` skill index
- Verification: `docs/plans/STAGE2-JADZIA-DONE.md`

## LEFT

- Commit jadzia-core Stage 2 artifacts (on Commander request)
- Push to `origin/master` when ready
- VPS deploy not executed (Zasada 11) — use `/jadzia-deploy` checklist when needed
- Untracked `Portfolio Vibe-codding/` — Commander decides keep/ignore

## RISKS

- VPS prod may differ from local until Commander runs `deployment/deploy-to-vps.sh`
- PRD paths (`/root/jadzia`) vs vps-ops example (`/opt/jadzia`) — confirm with Commander before deploy

## V-FILES

1. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\plans\STAGE2-JADZIA-DONE.md`
2. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\.cursor\skills\vibe-init\SKILL.md`
3. `C:\Users\FlexGrafik\FlexGrafik\github\WorkFlow\todo.json`
4. `C:\Users\FlexGrafik\FlexGrafik\github\WorkFlow\docs\handoffs\2026-05-23-vps-github-audit.md`

## NEXT_COMMAND_FOR_NEW_AGENT

```
@vibe-init Open app.flexgrafik.nl or execute WorkFlow S2-APP-01 per todo.json current_focus.
```
