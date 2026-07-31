# PRE-W6 Agent A — prod JWT dogfood notes

**Date:** 2026-07-31  
**URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w50a  
**VPS tip:** `94268f7` (matches plan)  
**Cache on page:** `vhq-w50a` (footer hint)

## API (localhost VPS, Bearer JWT)

- `GET /api/v1/commander/ops-bus/events` → total=2, enabled=true
- Event types: `lead_qualified` (EV-W5-001), `wizard_started` (EV-W5-002)
- Seeded via `POST /api/v1/commander/leads/10/disposition {acked}` → lead_qualified emit

## UI walk (Chrome DevTools, localStorage `coi_commander_jwt`)

| Room | Key observation |
|------|-----------------|
| Sales | JWT session active; cache vhq-w50a; Sales LIVE / Order PARKED strip |
| Wizard | **Operations Bus (typed)** — both bus cards visible |
| MC | Flow break: EV-W2-010 + `last bus: lead_qualified (L1/none)` |
| Order Desk | PARKED · EV-W2-010 · no LIVE desk |

## Screenshots

- jwt-00-sales.png
- jwt-01-wizard-bus.png
- jwt-02-mc.png
- jwt-03-order-parked.png

No runtime restart. No W6. No MKT commit.
