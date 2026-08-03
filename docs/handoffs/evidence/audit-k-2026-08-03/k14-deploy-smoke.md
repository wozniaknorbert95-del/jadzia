# K14 deploy smoke — 2026-08-03

| Field | Value |
|-------|-------|
| SHA | `bc2779c` |
| Host | VPS `/opt/jadzia` |
| Cache | `desk-dash10` |
| Backup | `/opt/jadzia/data/jadzia-pre-truth-recovery-20260803-190749.db` (integrity ok) |
| `systemctl is-active jadzia` | `active` |
| `/health` | `status: ok` |
| `/worker/health` | `healthy`, worker_loop_alive |
| `/commander/` | contains `desk-dash10`, SW `coi-commander-desk-dash10` |

Notes:
- VPS had dirty tracked tree; deploy used `git reset --hard origin/master` after SQLite backup.
- Live P0 still PARKED. GA4 live env not enabled (K2 remains fail-closed `unavailable` until separate GO).
