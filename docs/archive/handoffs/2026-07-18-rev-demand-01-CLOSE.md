# Handoff — REV-DEMAND-01 CLOSE (F0–F4)

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Status:** SUCCESS (code + tests; VPS deploy = Dowódca manual)  
**Parent:** `REV-DEMAND-01` → completed

## DONE

| Phase | ID | Result |
|-------|-----|--------|
| F0 | register | PASS — todo A+B intact |
| F1 | 01a dogfood | PASS local tests; VPS click via playbook |
| F2 | 01b widget CTA | PASS — deeplink + lead on email+consent |
| F3 | 01c disposition | PASS — API + Commander UI buttons |
| F4 | playbook | PASS — `docs/ops/JADZIA-REVENUE-DOGFOOD.md` |

### Code

- `agent/customer_agent.py` — CTA + optional `db_create_lead`
- `core/models.py` / `api/routes/chat.py` — response fields
- `agent/db.py` — `disposition` migration + `db_update_lead_disposition`
- `api/routes/commander.py` — `POST .../leads/{id}/disposition`
- `agent/commander/queue.py` — hide closed/snoozed hot leads
- `commander-ui/app.js` — Ack/Snooze/Close
- Tests: `test_widget_demand_cta.py`, `test_lead_disposition.py` (**PASS**)

## Active / parks

**Active next:** `REV-DEMAND-02` (F5 session durability) — pending  
**Parks unchanged:** REV-R0-02C Gate D, S1-01, OPS-FB-HYGIENE-01, B3-*, C1-01, D1-03

## STOP honored

No payment, no Mollie LIVE, no min199 change, no BFG/TikTok/B3 unpark, no autonomous deploy.

## NEXT

1. Dowódca: manual deploy `master` → run `JADZIA-REVENUE-DOGFOOD.md`
2. Agent: `REV-DEMAND-02` when ready (one gate)

```text
STATE: REV-DEMAND-01 F0-F4 code COMPLETE; deploy HITL
NEXT: REV-DEMAND-02 pending; parks preserved
SESSION_VERDICT: SUCCESS
```
