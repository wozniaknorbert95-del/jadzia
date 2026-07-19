# Handoff — REV-R0-02C READY for Gate D (COD OFF)

**Date:** 2026-07-18  
**Repo (ops):** zzpackage.flexgrafik.nl (WP prod CyberFolks)  
**Repo (meta):** jadzia-core  
**Prior:** `docs/handoffs/2026-07-18-rev-r0-02c-session-CLOSE.md`  
**Audit:** `zzpackage/docs/handoffs/2026-07-18-wp-wc-senior-audit.md`  
**Status:** `READY_FOR_GATE_D` pending Dowódca Mollie LIVE  
**GO-pack:** `docs/handoffs/2026-07-18-rev-r0-02c-gate-d-GO-pack.md` (preflight locked)  
**Session verdict:** SUCCESS

## DONE

### COD disabled (P0)
- WP option `woocommerce_cod_settings.enabled`: **yes → no**
- Title left as `Za pobraniem` (unused while disabled)
- Cache flushed: WP object cache + LiteSpeed purge all

### Checkout smoke (unpaid)
- URL: `https://zzpackage.flexgrafik.nl/afrekenen/`
- Payment radios: **only** `mollie_wc_gateway_ideal` (iDEAL, checked)
- Absent from page: `Za pobraniem`, Cash on delivery / COD
- WP-CLI available gateways: **only iDEAL**
- Evidence (outside Git): `Documents/REV-R0-02C/20-cod-off-CONFIRMED.txt`
- UI screenshot (repo): `zzpackage/docs/handoffs/_evidence/2026-07-18-cod-off-afrekenen-smoke.png`

### STOP honored
- Mollie **not** switched to LIVE (still TEST)
- No Gate D paid order placed
- No plugin / core updates
- No R1 / TikTok / BFG

## LEFT (Dowódca + next agent)

1. **Dowódca:** Mollie → **LIVE** (keys already present; Admin or WP option)
2. **Post-LIVE smoke (unpaid):** re-open `/afrekenen/` — still iDEAL-only (watch for extra Mollie methods)
3. **Gate D:** 1 authorized real paid iDEAL → WC `processing` + `_mollie_payment_mode=live` → Jadzia `classification=real` / `is_test=0` → bedankt GA4 purchase eligible
4. Merge PR jadzia #3 + zzpackage #74; close `REV-R0-02`
5. Optional later: Meta Pixel `is_test` gate, `WP_DEBUG` off, stale COD processing triage, plugin updates

## CRITICAL WARNINGS

- Mollie is still **TEST** — do **not** place Gate D order until LIVE confirmed.
- Do not bulk-update WP/WC plugins mid-Gate D.
- Do not replay GA4 history; no `--apply-classifications` without review.
- Stale COD processing backlog (29) — triage later, non-destructive; not required to start Gate D.

## NEXT SESSION START

```text
@blast REV-R0-02C Gate D LIVE paid order

Repo: jadzia-core + zzpackage
Cel: after Dowódca Mollie LIVE — 1 real paid iDEAL; WC↔Jadzia↔GA4 proof
STOP: bez plugin updates; bez R1/TikTok/BFG; bez GA4 history replay
Handoff: docs/handoffs/2026-07-18-rev-r0-02c-READY-for-Gate-D.md
Checklist: zzpackage/docs/checklists/REV-R0-02C-controlled-e2e.md
```

```text
STATE: COD OFF; checkout iDEAL-only; Mollie still TEST; Gate C PASS #3209
DEPLOY_STATE: Jadzia 504fdf6 LIVE; producer bfe8485 LIVE
NEXT: Dowódca Mollie LIVE → Gate D (1 real paid)
SESSION_VERDICT: SUCCESS
```
