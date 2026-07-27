---
status: "[CLOSED]"
title: "Deploy VPS 4cf66fe + budget freeze (no paid Meta)"
updated: "2026-07-27"
gate: "DEPLOY-GTM-TT"
---

# Handoff — 2026-07-27 Deploy + budget freeze

## Decyzja Dowódcy

- **Deploy kompleksowy** — GO (agent wykonuje VPS)
- **Nie publish** kampanii Meta €10/d
- **Zero ad spend** do **2026-08-06** (10 dni)

## DONE — Deploy VPS

| Check | Evidence |
|-------|----------|
| Git tip | **`4cf66fe`** @ `/opt/jadzia` |
| Service | `systemctl is-active jadzia` → **active** |
| Health local | `/worker/health` → **degraded** (ssh_connection=error — pre-existing) |
| Health public | `https://api.zzpackage.flexgrafik.nl/worker/health` → **200 OK** |
| TT-PUB kod | `agent/publishers/tiktok.py` → **OK** on VPS |
| SQLite backup | `jadzia-pre-rev-demand-01-20260727-143731.db` |

### Deploy fix (RCA)

`git clean` usunął `/opt/jadzia/output` i `/opt/jadzia/secrets` → systemd **226/NAMESPACE**.  
Naprawa: `mkdir -p output secrets` + `chown jadzia` + restart.

## DONE — Strategy update

- [GTM-1PAGER.md](../ops/marketing/GTM-1PAGER.md) — budget freeze · organic #1
- [META-FINAL-CHECKLIST.md](../ops/marketing/META-FINAL-CHECKLIST.md) — **PARKED** do 2026-08-06
- [OPERATOR-TODAY.md](../ops/marketing/OPERATOR-TODAY.md) — priorytet organic + TT

## NOT DONE (świadomie)

| Item | Why |
|------|-----|
| Meta paid publish | Budget freeze — **€0** do 2026-08-06 |
| TT E2E publish | Needs `TIKTOK_ACCESS_TOKEN` HITL (S6) |
| Mollie / Purchase | Out of scope |

## NEXT (Dowódca — €0 tor)

1. **Asset** — `MKT/YYYY-WW/` master + `tt_hook_15s`
2. **FB organic** — Commander HITL publish
3. **TT Developer** — token + verified URL → VPS `.env` (S6)
4. **Po 2026-08-06** — [META-FINAL-CHECKLIST](../ops/marketing/META-FINAL-CHECKLIST.md) → paid €10/d

## STOP

Ads spend · Mollie LIVE · Studio spam bez E2E · fake PASS.
