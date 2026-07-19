# Handoff — OPS-FB-HYGIENE-01 READY for human

**Date:** 2026-07-18  
**Owner:** Dowódca (human)  
**Status:** `ready_for_human`  
**Agent role:** checklist only — no autonomous FB delete / secret rotate

## Why

Smoke/test FB posts from Marketing E2E should be removed from the Page when convenient. Optional: rotate App Secret if exposure risk.

## Checklist (Dowódca)

1. Facebook Page → identify smoke/test posts (text/photo/video from Jadzia E2E, e.g. known proof entries).
2. Delete or archive those posts in Meta UI (or Graph API with Page token — **you** run it).
3. Optional: Meta App → rotate App Secret → update VPS `.env` → restart `jadzia.service` (manual deploy rule).
4. Reply in VCMS/handoff: `OPS-FB-HYGIENE-01 DONE` with count deleted (no tokens in chat).

## STOP

- Agent must not delete Page posts autonomously in this gate.
- Do not mix with Gate D / Mollie / revenue apply-classifications.
- Do not commit secrets.

## Related

- `todo.json` → `OPS-FB-HYGIENE-01`
- Brief HITL may nudge this weekly via `ops_fb_hygiene_nudge` tickets
