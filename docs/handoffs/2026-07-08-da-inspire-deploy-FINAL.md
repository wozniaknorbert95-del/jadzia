# Handoff: INSPIRE v2 / Design Agent — Deploy FINAL (2026-07-08)

**Gate:** Operator deploy — **CLOSED**  
**Scope:** Design Agent mockups (INSPIRE v2) — **separate from COI spine**  
**Live:** https://zzpackage.flexgrafik.nl/voertuigreclame-ontwerp/

## Completed

| Step | Status |
|------|--------|
| Merge `feat/design-agent-inspire-v2` → main + push (`20f58ec`) | PASS |
| Deploy jadzia INSPIRE on VPS (engine + OCR + env) | PASS |
| GHA deploy WP (run 28947243024) | PASS |
| Smoke API HTTPS tier B/A (`design-agent-g2-smoke.json`, HTTP 200, €0.22) | PASS |
| `FG_DESIGN_AGENT_API_ENABLED=true` in wp-config.php | PASS |
| Playwright strict UI (`p0=0`, `apiEnabled=true`) | PASS |

## Fixes during deploy

- jadzia crash — SCP as root → `chown jadzia:jadzia` (import `agent.inspire` failed)
- tier-matrix — missing path on VPS → upload + `DA_TIER_MATRIX_PATH`
- vehicle templates — missing PNG → `/opt/zzpackage/theme-assets/images/` + `ZZPACKAGE_THEME_ASSETS`
- 502/500 — missing `FAL_KEY` / `OPENROUTER` in `.env` → filled from local sources

## Open (P1, non-blocking)

- POLISH-06 — E2E wizard `?highlight=MA-005`
- Full GPT→generate Playwright E2E — separate ticket
- VPS jadzia git sync (code via SCP; sync repo when convenient)
- LiteSpeed Purge All in WP admin if cache stale

## Rollback (< 5 min)

In `wp-config.php`:
```php
define('FG_DESIGN_AGENT_API_ENABLED', false);
```

## COI note

Design Agent is **not** the Commander's daily Jadzia interface. COI ops = Telegram + worker API — see `docs/ops/JADZIA-OPERATOR-PLAYBOOK.md`.
