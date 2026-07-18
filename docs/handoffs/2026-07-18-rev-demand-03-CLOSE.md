# Handoff — REV-DEMAND-03 INSPIRE → lead bridge

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**FEATURE_SHA:** `367549f` (INSPIRE→lead code)  
**TIP_SHA:** `66a4aad` (docs tip after LIVE close)  
**VPS:** `/opt/jadzia` @ **TIP_SHA** `66a4aad`, `jadzia.service` **active**  
**Backup:** `/opt/jadzia/data/jadzia-pre-rev-demand-01-20260718-101131.db` (integrity ok)  
**Status:** SUCCESS — LIVE  
**Session verdict:** SUCCESS  
**Owner:** Revenue / Demand senior slice

## DONE

| Item | Result |
|------|--------|
| Persist | email+consent → `db_create_lead(source=inspire)` |
| Soft-fail | DB errors do not break chat turn |
| API | `DesignAgentChatResponse.lead_id` |
| Tests | 5 unit + design chat green |
| Deploy | FEATURE `367549f`; widget CTA smoke still OK |
| VPS smoke | `SMOKE_OK True` — lead `source=inspire`, name set |
| Backlog | `REV-DEMAND-03` **completed** |

## DEPLOY_STATE

```text
FEATURE_SHA: 367549f
TIP_SHA: 66a4aad
VPS: /opt/jadzia @ TIP_SHA active
```

## LEFT

1. Control Truth / phone hub — see `docs/handoffs/2026-07-18-ssot-demand-CLOSE.md`
2. `REV-DEMAND-04` after `COI-CMD-MOBILE-01` LIVE

## CRITICAL WARNINGS

- No Gate D / Mollie LIVE / min199 / live charge
- Do not delete parks; do not ship `_recover_*.py`
- Health `ssh_connection=error` pre-existing

## NEXT SESSION START

Superseded by Plan1 Control Truth / Plan2 mobile hub. Canonical blast in:

`docs/handoffs/2026-07-18-ssot-demand-CLOSE.md`
