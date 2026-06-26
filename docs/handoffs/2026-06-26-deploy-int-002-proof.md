# DEPLOY-01 proof — INT-002 E2E (wypełnij po deploy)

**Date:** _YYYY-MM-DD_  
**Gate:** DEPLOY-01  
**Status:** _PASS | FAIL_

## Checklist

- [ ] Smoke curl `SMOKE-1` → `db_status: success`
- [ ] Mollie test order → real WC `order_id` in `orders`
- [ ] zzpackage log: `[FG Jadzia] Webhook OK`
- [ ] jadzia log: `[OrderNode] Order saved`

## Proof (bez PII)

| Field | Value |
|-------|-------|
| smoke_order_internal_id | _e.g. 1_ |
| e2e_wc_order_id | _e.g. 12345_ |
| e2e_db_row_status | _processing / completed_ |
| deploy_jadzia_commit | _git sha_ |
| deploy_theme_date | _date_ |

## DB query output (redacted)

```
_paste sqlite3 SELECT result — no email_
```

## Meta sync (po PASS)

W `flexgrafik-meta/docs/core/integration-contracts.md`:

- INT-002 Status → **LIVE**
- Endpoint → implemented
- Trusted sources → aktualne ścieżki jadzia + zzpackage

## todo.json update

```json
"active_gate": null,
"DEPLOY-01": "completed",
"P1-02": "pending"
```

---
CURRENT_STAGE: _L4-Closed after PASS_
RECOMMENDED_NEXT: P1-02 analytics_node OR DEPLOY-02 leads E2E
