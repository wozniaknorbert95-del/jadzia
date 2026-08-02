---
gate: DEMAND-DESK-DEPLOY-00
status: CLOSE
updated: 2026-08-02
go: "GO DEPLOY COMMANDER UI"
---

# CLOSE — Commander UI deploy + prod UX audit

## Deploy

| Pole | Wartość |
|------|---------|
| TIP prod | **4f12428** |
| SHA dashboard | c4d9334 |
| SHA hotfix | 4f12428 (memory RO set-now) |
| URL | https://api.zzpackage.flexgrafik.nl/commander/?view=demand-desk&cb=desk-dash02 |
| HEALTH | OK · jadzia active |

## Pre-deploy verify

- doctor PASS
- 50 desk tests PASS

## Hotfix during deploy

`GET /demand-os/status` → 500 on VPS (read-only `docs/.../MEMORY.json`).  
Fixed in `4f12428`: fallback `data/demand-os/MEMORY.json` + non-fatal save.

## Prod UX audit (agent, JWT)

| Check | Result |
|-------|--------|
| desk-dash02 served | PASS |
| Deep link demand-desk | PASS |
| B→A DOM order | PASS |
| Design §8 link | PASS |
| VHQ CTA Biuro Popytu | PASS |
| API status authed | PASS |
| Odśwież + JWT | PASS (persists) |
| Top assets empty state | PASS (honest, no fake) |
| Hunt dry list | PASS (allowlist rows) |
| Doctor/Gate/Kontrakt | PASS (OK / v2.1.1) |
| Marketing tab separate | PASS |

## STOP

Marketing HITL live · Ads · Mollie — still PARKED_LAST until separate GO.

## Next human

1. Telegram login smoke on phone
2. Optional: sync set-now fixtures to VPS for richer KPI (not blocking)
3. `GO MARKETING HITL` when ready
