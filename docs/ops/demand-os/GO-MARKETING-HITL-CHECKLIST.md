---
status: "[READY_FOR_HUMAN · GO ceremony]"
title: "GO MARKETING HITL — Founder checklist"
updated: "2026-08-03"
gate: "DEMAND-OS-MARKETING-4-00"
master_todo: "docs/ops/demand-os/MASTER-TODO-4.md"
prerequisite: "Etap 5f SEALED · go_day_ready 100%"
---

# GO MARKETING HITL — checklist

**Jedyna ścieżka unpark marketing live.** Agent nie wykonuje bez tego GO.

## Pre-flight (agent PASS 2026-08-03)

- [x] Etap 5f SEALED · Hard DoD 15/15
- [x] HITL-READY dry PASS
- [x] go_day_ready score **100%**
- [x] Env switch `DEMAND_OS_MARKETING_HITL=GO` (kod gotowy)
- [x] Ads **PARK cash** · ADS-FREEZE active
- [x] First asset Val PASS: `tt_w32_install_01`

## Founder GO (wpisz datę + initial)

```
GO MARKETING HITL
Date: ___________
By: Dowódca
Scope: organic HITL only (TT + FB hunt + blog) · NO Ads
```

- [x] Founder GO wpis — `2026-08-03-GO-MARKETING-HITL.md`
- [x] VPS deploy `2f68b64` + env GO — 2026-08-03
- [x] Prod verify gate READY — browser + VPS

## Ops (po GO — VPS)

- [ ] `DEMAND_OS_MARKETING_HITL=GO` w `/opt/jadzia/.env`
- [ ] `systemctl restart jadzia`
- [ ] Verify: `marketing_hitl_gate: READY` w Desk / status API
- [ ] Desk: brak bannera „PARKED - EUR nie powstaje…”

## First actions (PARKED until UNLOCK)

> **env GO ≠ cadence unlock.** Day-1 publish is **PARKED**.  
> Unlock ceremony: [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md)

- [ ] ~~TT HITL publish~~ — PARKED until unlock record
- [ ] ~~FB hunt live~~ — PARKED until unlock record
- [ ] ~~Blog ship~~ — PARKED until unlock record
- [ ] After unlock: LEDGER `publish=Y` only for REAL actions

## STOP

- Meta/Google Ads
- Live bez Val PASS + pass_token
- Multi-CTA / spam
- VPS deploy bez GO powyżej

Evidence close: `docs/handoffs/DEMAND-MARKETING-4-CLOSE.md` (po P2)
