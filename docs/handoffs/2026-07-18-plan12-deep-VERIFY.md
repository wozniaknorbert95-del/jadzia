# Verify — Plan1+Plan2 deep check (pre REV-DEMAND-04)

**Date:** 2026-07-18  
**Verdict:** **GO for next session REV-DEMAND-04** (after this docs sync)  
**Verified tip:** `7aa32d8`  
**FEATURE UI:** `87d7912`

## Matrix

| Check | Result |
|-------|--------|
| local=origin=VPS at verify | PASS `7aa32d8` |
| LIVE tip pointer was stale `735c2b4` | **FIXED** → verified tip policy |
| Health worker+sqlite | PASS (`ssh=error` known) |
| Widget CTA deeplink | PASS |
| Durability SQLite row | PASS |
| INSPIRE source=inspire | PASS |
| `/commander/` 200 + map + bottom-nav | PASS |
| css/js 200 | PASS |
| ADR D0.6 present | PASS |
| single `showView` | PASS |
| `_recover_*` absent | PASS |
| Parks statuses | PASS (unchanged) |
| `active_gate` | `REV-DEMAND-04` |
| Commander disposition UI | still `ready_for_human` (JWT) |
| Zero Mollie | PASS (no charge path) |

## Gap fixed this verify

- Tip drift in AGENTS/todo/brain/CLOSE (`735c2b4` vs real `7aa32d8`)
- Policy: tip SoT = VPS `git rev-parse`; stop tip-chase loop

## STOP

Do **not** start coding REV-DEMAND-04 in this verify commit. Next session blast only.
