# W6 prod JWT dogfood — Approval Vault

**Date:** 2026-07-31  
**URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w60a  
**VPS tip (runtime):** `06212d7`  
**Cache:** `vhq-w60a`

## API (VPS localhost, Bearer JWT)

- Seed L2 companion + L3 STOP via `emit_ops_bus_event`
- `POST .../approval` L2 → `ok` · `side_effects=false`
- `POST .../approval` L3 → **403** Founder GO required
- Pending after: L3 only (`total=1`)

## UI walk (Chrome DevTools, `coi_commander_jwt`)

| Room | Key observation |
|------|-----------------|
| Approval Vault | L3 STOP card · **0 Approve buttons** · cache `vhq-w60a` |
| Order Desk | **PARKED · EV-W2-010** · no LIVE desk |

## Screenshots

- `prod-w60-01-vault.png`
- `prod-w60-02-order.png`

No Ads/Mollie. No MKT. JWT temps wiped after dogfood.
