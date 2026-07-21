# Handoff — AUD-REM-INGRESS-01 Public ingress hardening

**Date:** 2026-07-21  
**Task:** `AUD-REM-INGRESS-01`  
**Status:** LOCAL PASS · GitHub Actions and VPS unverified  
**Git:** dirty shared `master` worktree · no commit, no push, no deploy

## Closed controls

1. Widget chat accepts at most 8 KiB before parsing and bounded non-empty
   messages. It mints a UUIDv4 session for a missing, malformed, expired, or
   unknown client session, registers it in SQLite, and returns that identifier
   to the caller. Existing issued sessions retain their history.
2. Widget rate limiting is SQLite-backed, keyed by a salted hash of client and
   session, and persists across process restarts. The default is 30 messages
   per hour; excess requests receive `429` plus `Retry-After`.
3. Telegram native updates now require
   `X-Telegram-Bot-Api-Secret-Token` whenever `TELEGRAM_WEBHOOK_SECRET` is
   configured. Update-ID replay claiming is durable in SQLite before any
   response side effect. Native bodies are capped at 64 KiB.
4. Brain Bus requires a bounded `correlation_id`, rejects malformed or
   oversized bodies/payloads, and claims each source/correlation pair in
   SQLite before enqueueing. A duplicate returns an acknowledgement without
   re-enqueueing or processing.
5. Production configuration hides `/docs`, `/redoc`, and `/openapi.json`
   unless the explicit `PUBLIC_API_DOCS_ENABLED=1` opt-in is set. Development
   metadata remains available.

## Evidence

```text
uv run --locked python -m pytest \
  tests/test_ingress_hardening.py tests/test_customer_chat.py \
  tests/unit/test_mb_f3_brain_bus.py tests/test_telegram_bot.py -q
```

Result: `41 passed`.

```text
uv run --locked python -m pytest tests/ -q
```

Result: `643 passed, 17 skipped, 1 xfailed` in 108.54 s.

```text
uv run --locked ruff check api/ingress.py tests/test_ingress_hardening.py
uv run --locked black --check api/ingress.py tests/test_ingress_hardening.py
git diff --check
```

Result: PASS.

## Negative coverage

- unknown widget session is replaced; issued session continuity is retained;
  oversize widget bodies stop before LLM invocation; rate exhaustion is `429`;
- missing/wrong native Telegram secret is rejected, and the same update ID
  remains claimed after reopening the SQLite connection;
- oversized Telegram request is `413`; missing or oversized Brain Bus event is
  `422`; a repeated Brain Bus correlation is acknowledged but not enqueued;
- production docs, Redoc, and OpenAPI all return `404`.

## Residual / next

- Browser client integration must retain the `session_id` returned by the
  widget response before production deployment. This task did not deploy or
  exercise the external widget.
- CI and VPS remain unverified until an explicit commit/push and separate GO.
- **Next session (Dowódca):** `AUD-REM-GIT-DEPLOY-01` — git hygiene + Actions +
  deploy checklist for the whole Wave1–Wave2 batch. See
  `docs/handoffs/2026-07-21-AUD-REM-GIT-DEPLOY-READY.md`. `AUD-REM-WRITE-01`
  resumes after ship or explicit re-prioritize.
