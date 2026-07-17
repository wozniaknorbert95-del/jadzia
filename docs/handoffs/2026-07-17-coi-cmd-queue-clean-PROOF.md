# PROOF — COI-CMD-QUEUE-CLEAN (2026-07-17)

**Commit:** `33e58b9` (+ follow-up docs)  
**VPS:** `/opt/jadzia` @ `33e58b9`, `jadzia` active

## Actions

1. DB backup before cleanup
2. Dry-run: 3 E2E leads matched
3. Apply: deleted ids 1–3
4. Remaining leads: `jan@bouw.com`, `bob@gamil.com`

## Match rules

- `email LIKE deploy02-%`
- `email LIKE int004-e2e-%`

## Script

`deployment/cleanup-e2e-hot-leads.py --dry-run | --apply`

## Note

VPS had dirty working tree; stashed as `vps-pre-queue-clean-20260717` then `reset --hard origin/master`.
