# Handoff — Repo hygiene & segregation (2026-06-30)

**Task:** Repo cleanup session (no features, no deploy)  
**Classification:** REFACTOR / hygiene  
**Status:** DONE

## Summary

Restored canonical pointers for `/vibe-init`, removed security risk, purged root clutter, and archived completed plans + duplicate handoffs.

## Actions taken

### Security (P0)
- **DELETED** `list_models.py` (hardcoded Google API key)
- **ACTION REQUIRED (Dowódca):** Rotate the exposed key in Google Cloud Console

### Canonical sync (P1)
- `AGENTS.md` → active plan = `PLAN-COI-PHASE-B.md`
- `brain.md` §6 content calendar 45%, §7 active plan Phase B, §10 handoff index
- `docs/PRD-core.md` → `/opt/jadzia`, Phase B active

### Root purge (P2)
| Action | Item |
|--------|------|
| DELETE | `agent.py` (legacy), `test_chat.py`, `test_models_vps.py`, `agent/agent.py.backup`, `data.backup.20260117_091114/` |
| MOVE OUT | `Portfolio Vibe-codding/` → `Desktop/Portfolio-Vibe-codding/` |
| ARCHIVE | `Project-Instructions.md`, `functions.php` → `docs/archive/legacy/` |

### Docs archive (P3)
- Created `docs/archive/{plans,handoffs,legacy}/` + `docs/archive/README.md`
- **7 plans** → `docs/archive/plans/` with `status: COMPLETED`
- **24 handoffs** → `docs/archive/handoffs/`
- **Active handoffs:** 10 + README + 2 templates (≤15 target met)
- **Index:** `docs/handoffs/README.md`

### Deployment
- One-offs → `deployment/archive/` (`deploy01-wc-order-smoke.sh`, `vps-post-deploy-int002.sh`)
- Untracked scripts kept: `migrate-to-opt.sh`, `verify-ga4-zzpackage.sh`, `deploy-b2-calendar-e2e.sh`

### `.gitignore`
Added: `data.backup*/`, `*.backup`, `logs/`, `.pytest_cache/`, `Portfolio*/`

## Verification

```
pytest tests/ -q  → 342 passed, 1 skipped, 1 xfailed
```

## KEEP (active in repo)

**Plans:** `PLAN-COI-PHASE-B.md`, `blast-b3-facebook-publish.md`, `PLAN-OPTIMATE-GCP-JADZIA.md`  
**Canonical:** `brain.md`, `todo.json`, `AGENTS.md`, `docs/PRD-core.md`  
**Handoffs:** see `docs/handoffs/README.md`

## Not done (by design)

- No commit (await Dowódca)
- No deploy (Zasada 11)
- No flexgrafik-meta edits
- `functions.php` archived locally — restore to zzpackage theme if needed (canonical: `inc/integrations/fg-jadzia-order-webhook.php`)

## Next session

Per `todo.json`: **D1-03** EN docstrings OR provide FB Page Access Token for B.3.
