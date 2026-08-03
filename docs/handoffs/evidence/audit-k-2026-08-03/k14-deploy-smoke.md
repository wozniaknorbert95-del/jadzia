# K14 deploy smoke — Audit Partial Closeout 2026-08-03

| Field | Value |
|-------|-------|
| SHA | `c04d1b4` |
| Host | VPS `/opt/jadzia` |
| Cache | `desk-dash11` |
| Backup | `/opt/jadzia/data/jadzia-pre-partial-closeout-20260803-194331.db` |
| `systemctl is-active jadzia` | `active` |
| `/health` | `status: ok` |
| `/commander/` | contains `desk-dash11` |

Notes:
- Deploy: SQLite backup → `git reset --hard origin/master` → restart → smoke.
- Live P0 still PARKED.
- K2: env path for GA4 SA set but file absent → fail-closed `unavailable`; live metric blocked on credentials (no fake sessions).
- Ledger-export.timer artifact committed; **not** enabled (needs separate GO).
