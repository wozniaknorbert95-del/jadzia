# Handoff — AUD-REM batch ready for git/deploy pipeline

**Date:** 2026-07-21  
**Parent:** `AUD-REM-00`  
**Status:** LOCAL PASS batch · **NO COMMIT · NO PUSH · NO DEPLOY**  
**Git tip (committed):** `master` @ `29043cb`  
**Worktree:** dirty — all Wave 1–2 remediation local only

## Verification (this close)

| Check | Result |
|-------|--------|
| `tests/test_ingress_hardening.py` | **7 passed** (re-run 2026-07-21) |
| Full suite (prior INGRESS close) | **643 passed, 17 skipped, 1 xfailed** |
| Production | **UNVERIFIED** |
| GitHub Actions | **unverified** (nothing pushed) |
| VPS / deploy | **not started** (`standing_go_closeout=false`) |

## Locally completed remediation (uncommitted)

| Task | Finding | Evidence handoff |
|------|---------|------------------|
| `AUD-REM-CI-01` | F-01 fake green CI | `2026-07-21-AUD-REM-CI-01-CLOSE.md` |
| `AUD-REM-QUALITY-01` | F-11 quality workflow truth | `2026-07-21-AUD-REM-QUALITY-01-CLOSE.md` |
| `AUD-REM-CALLBACK-01` | F-02 SSRF callback | `2026-07-21-AUD-REM-CALLBACK-01-CLOSE.md` |
| `AUD-REM-SSH-01` | F-03 / F-09 SSH trust | `2026-07-21-AUD-REM-SSH-01-CLOSE.md` |
| `AUD-REM-DEPS-01` | F-05 lock + Chroma | `2026-07-21-AUD-REM-DEPS-01-CLOSE.md` |
| `AUD-REM-INGRESS-01` | F-07 ingress abuse | `2026-07-21-AUD-REM-INGRESS-01-CLOSE.md` |

## Dirty worktree inventory (for git cleanup)

**Do NOT commit blindly.** Split by concern. Exclude noise: `.coverage`, `coverage.xml`, `.cursor/session-state.md`, `.venv`, caches.

### Security / API (commit candidates)

- `api/ingress.py` (new), `api/routes/chat.py`, `api/routes/brain_bus.py`, `api/telegram.py`, `api/app.py`, `api/webhooks.py`
- `core/webhook_url_guard.py` (new), `core/models.py`
- `agent/db.py`, `agent/telegram_validator.py`, `agent/marketing/brain_bus.py`
- `agent/tools/ssh_host_policy.py`, `agent/tools/safe_archive.py`, `agent/tools/ssh_pure.py`, `agent/tools/ssh_orchestrator.py`, `agent/tools/wp_explorer/ssh_connector.py`

### Supply chain / CI

- `pyproject.toml`, `requirements.txt`, `requirements.lock`, `uv.lock` (if present)
- `.github/workflows/ci.yml`, deleted `.github/workflows/tests.yml`
- `.env.example` (non-secret docs only)

### Tests / contracts

- `tests/test_ingress_hardening.py`, `tests/test_dependency_lock_contract.py`, `tests/test_ci_gate_contract.py`, `tests/test_quality_workflow_contract.py`
- `tests/unit/test_ssh_security.py`, `tests/unit/test_webhook_url_guard.py`
- Related test updates under `tests/`

### Docs / ops SoT

- `docs/ops/JADZIA-CORE-AUDIT-2026-07-21.md`
- `docs/handoffs/2026-07-21-*` (audit + remediation closes)
- `todo.json`, `.agents/workflows/jadzia-test.md`

### Park / do not mix without review

- `deployment/mkt-dash01-verify.sh`, `docs/handoffs/2026-07-19-SESSION-CLOSE-MKT-DASH.md`
- Design-agent / organic CEO test edits if unrelated to remediation intent

## Next session goal (Dowódca GO)

**TASK:** `AUD-REM-GIT-DEPLOY-01` — kompletny pipeline:

1. **Git hygiene:** inventory → staged logical PR(s) or stacked commits (prefer 1 PR per wave or one reviewable mega-PR with clear sections — decide 1 path).
2. **Pre-push gate:** full `pytest`, `uv lock --check`, `pip-audit`, scoped lint of touched files.
3. **Commit + push** only after explicit Dowódca GO for commit.
4. **GitHub Actions** verify green on tip.
5. **Deploy plan** (Zasada 11): checklist env (`TELEGRAM_WEBHOOK_SECRET` as native header, `WIDGET_CHAT_RATE_LIMIT`, `PUBLIC_API_DOCS_ENABLED`, `GITLEAKS_LICENSE` if org, SSH known_hosts/fingerprint HITL, widget frontend must store returned `session_id`).
6. **VPS** only after **fresh GO** — no autonomous deploy.

**Hard STOP:** secrets in commits, force-push, Gate D/Mollie, fake PASS, mixing WRITE/HEALTH/DB into same deploy without evidence.

## Residual remediation (after or parallel to deploy)

- `AUD-REM-WRITE-01` … `AUD-REM-VPS-VERIFY-01` remain open per program handoff.
- Widget frontend (zzpackage) must consume server-issued `session_id`.

## Start prompt for new session

See CORE block `NEXT_COMMAND_FOR_NEW_AGENT` below.
