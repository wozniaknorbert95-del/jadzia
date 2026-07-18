# Handoff — REV-DEMAND-03 INSPIRE → lead bridge

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Status:** GO authorized — commit+redeploy in progress  
**Owner:** Revenue / Demand senior slice

## DONE (pre/post deploy)

| Item | Result |
|------|--------|
| Persist | email+consent → `db_create_lead(source=inspire)` |
| Soft-fail | DB errors logged; chat turn still returns |
| API | `DesignAgentChatResponse.lead_id` |
| Tests | 5 inspire lead + design_agent_chat green |
| Prior | 02 LIVE (widget session durability) |

## STOP

No Gate D / Mollie / min199. Parks untouched. No `_recover_*`.

## Next after LIVE

**REV-DEMAND-04** brief HITL → sales actions.
