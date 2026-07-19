# Handoff: INSPIRE v2 Design Agent deploy FINAL (2026-07-08)

**Gate:** Operator deploy — **CLOSED**  
**Track:** Separate from COI spine (Design Agent product)

## Deploy summary

| Step | Status |
|------|--------|
| Merge `feat/design-agent-inspire-v2` → main + push | **PASS** @ `20f58ec` |
| Deploy jadzia INSPIRE on VPS (engine + OCR + env) | **PASS** |
| GHA deploy WP | **PASS** run `28947243024` |
| Smoke API HTTPS tier B/A | **PASS** `docs/ops/design-agent-g2-smoke.json` HTTP 200, €0.22 |
| `FG_DESIGN_AGENT_API_ENABLED=true` | **PASS** wp-config.php |
| Playwright strict UI | **PASS** p0=0, apiEnabled=true |

## Live

- https://zzpackage.flexgrafik.nl/voertuigreclame-ontwerp/
- Hero: „Ontwerp je bus — gratis”, `apiEnabled: true`

## Fixes during deploy

| Issue | Fix |
|-------|-----|
| jadzia crash (SCP as root) | `chown jadzia:jadzia` — `import agent.inspire` failed |
| tier-matrix missing on VPS | upload + `DA_TIER_MATRIX_PATH` |
| vehicle templates missing | `/opt/zzpackage/theme-assets/images/` + `ZZPACKAGE_THEME_ASSETS` |
| 502/500 missing keys | `FAL_KEY` / `OPENROUTER` added to `.env` |

## Rollback (< 5 min)

In `wp-config.php`: `define('FG_DESIGN_AGENT_API_ENABLED', false);`

## Open P1 (non-blocking)

- POLISH-06 — E2E wizard `?highlight=MA-005`
- Playwright full GPT→generate E2E — separate ticket
- VPS jadzia git sync vs SCP — see spine closure F1
- LiteSpeed Purge All if cache stale

## References

- Gate status: `docs/ops/inspire-v2/audit/DEPLOY-GATE-STATUS.md` (zzpackage repo if present)
- Smoke: `docs/ops/design-agent-g2-smoke.json` (zzpackage repo if present)
