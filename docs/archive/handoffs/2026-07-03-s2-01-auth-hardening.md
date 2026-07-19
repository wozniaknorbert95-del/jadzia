# Handoff: S2-01 Prod Auth Hardening (2026-07-03)

**Task:** S2-01-PROD-AUTH-HARDENING  
**Status:** CODE COMPLETE — deploy pending (Zasada 11)

## Delivered

| Area | Change |
|------|--------|
| `core/config.py` | `REQUIRE_SECRETS` / `JADZIA_ENV=production` startup gate |
| `api/dependencies.py` | JWT required when secrets mode; fail if JWT missing in prod |
| `api/routes/webhooks.py` | HMAC mandatory in prod mode |
| `api/routes/leads.py` | X-API-Key mandatory in prod mode |
| Admin routes | JWT on `/chat`, `/rollback`, `/clear`, `/logs`, `/test-ssh`, `/sessions`, `/costs` |
| `.env.example` | Full INT + prod gate vars |
| `docs/PRD-core.md` | Security section + status sync |
| Tests | `tests/unit/test_auth_hardening.py` (+13 tests) |

## Verify (local)

```
pytest tests/ → 376 passed
```

## VPS deploy checklist

See [`2026-07-03-s2-01-deploy-checklist.md`](2026-07-03-s2-01-deploy-checklist.md)
