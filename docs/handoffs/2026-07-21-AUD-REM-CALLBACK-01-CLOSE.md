# Handoff — AUD-REM-CALLBACK-01 worker callback SSRF

**Date:** 2026-07-21  
**Task:** `AUD-REM-CALLBACK-01`  
**Status:** LOCAL PASS · GitHub Actions unverified (no commit, no push, no deploy)  
**Scope:** outbound worker callback validation and SSRF controls

## Decision

Worker callbacks are now disabled by default and must target an HTTPS hostname
listed in `WEBHOOK_CALLBACK_ALLOWLIST`. The hostname is resolved before use and
every resolved address must be globally routable. Redirects are not followed,
and callback logs contain only the scheme, host, and port.

New requests are rejected at the Pydantic/API boundary. Persisted legacy task
payloads are checked again immediately before the outbound request.

## Changes

1. Added `core/webhook_url_guard.py`:
   - HTTPS-only callback URLs with a 2,048-character maximum;
   - host allowlist via `WEBHOOK_CALLBACK_ALLOWLIST`;
   - rejection of private, loopback, link-local, reserved, and otherwise
     non-global resolved IP addresses;
   - log-safe callback target redaction.
2. `WorkerTaskRequest` validates callback URLs before queue insertion.
3. `api.webhooks.notify_webhook()` revalidates persisted URLs, uses
   `follow_redirects=False`, rejects redirect responses, and avoids logging URL
   paths, query strings, credentials, or exception text.
4. `.env.example` documents the callback allowlist.
5. Added SSRF regression tests, including API 422 before queueing, private DNS,
   private literal IPs, non-HTTPS schemes, redirect blocking, and log redaction.

## Evidence

```text
ruff check core/webhook_url_guard.py api/webhooks.py tests/test_webhooks.py tests/unit/test_webhook_url_guard.py
black --check core/webhook_url_guard.py api/webhooks.py tests/test_webhooks.py tests/unit/test_webhook_url_guard.py
python -m pytest tests/test_webhooks.py tests/unit/test_webhook_url_guard.py -q
```

Result: scoped Ruff/Black PASS; `16 passed`.

```text
python -m pytest tests/ -v --cov=agent --cov=api --cov=core --cov=cli --cov-report=term-missing --cov-report=xml:coverage.xml
```

Result: `624 passed, 17 skipped, 1 xfailed, 861 warnings in 109.67s`;
real `coverage.xml` written; total coverage `63%`.

## Residual risk

- Every legitimate callback host must be explicitly added to
  `WEBHOOK_CALLBACK_ALLOWLIST`; otherwise it is rejected by design.
- Callback DNS is validated at request validation and again immediately before
  dispatch. The control does not claim VPS runtime verification.
- GitHub Actions on Python 3.11 remains unverified until an explicit commit and
  push. Production remains `UNVERIFIED`.

## Next

Start `AUD-REM-SSH-01` only as a separate 1-1-1 task: known-host policy and
fingerprint pinning, followed by safe list/archive operations with negative
MITM/path-traversal tests. A production host fingerprint requires human/VPS GO.
