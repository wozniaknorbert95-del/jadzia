# Handoff — AUD-REM-GIT-DEPLOY-01 Git / CI / deploy pipeline

**Date:** 2026-07-21  
**Task:** `AUD-REM-GIT-DEPLOY-01`  
**Status:** **DEPLOY-READY** · awaiting Dowódca **GO** (commit/push) · **NO VPS DEPLOY**  
**Git tip (committed):** `master` @ `29043cb`  
**Worktree:** dirty — Wave1–Wave2 batch staged for one PR

## Decyzja (1 ścieżka)

**Jeden przeglądany PR** `feat/audit-remediation-wave1-2` → `master`, 6 logicznych commitów (reviewable sections), bez split A/B. Park poza PR: `deployment/mkt-dash01-verify.sh`, `docs/handoffs/2026-07-19-SESSION-CLOSE-MKT-DASH.md`.

## Inwentaryzacja dirty tree vs `29043cb`

**Baseline:** `29043cb76aea934ab74d263655383f0787876311`  
**Stat (bez noise):** ~45 plików śledzonych + 4 nowe moduły + `uv.lock`  
**Wykluczone z commita:** `.coverage`, `coverage.xml`, `.cursor/session-state.md`, `.venv`, caches

### W PR (remediation batch)

| Warstwa | Pliki |
|---------|-------|
| **F-01 CI** | `.github/workflows/ci.yml`, deleted `tests.yml`, `tests/test_ci_gate_contract.py` |
| **F-11 Quality** | `.agents/workflows/jadzia-test.md`, `tests/test_quality_workflow_contract.py` |
| **F-02 Callback** | `core/webhook_url_guard.py`, `core/models.py`, `api/webhooks.py`, `tests/unit/test_webhook_url_guard.py`, test updates |
| **F-03/F-09 SSH** | `agent/tools/ssh_host_policy.py`, `safe_archive.py`, `ssh_pure.py`, `ssh_orchestrator.py`, `wp_explorer/ssh_connector.py`, `tests/unit/test_ssh_security.py` |
| **F-05 Deps** | `pyproject.toml`, `requirements.txt`, `requirements.lock`, **`uv.lock`**, `.gitignore` (`!uv.lock`), `tests/test_dependency_lock_contract.py`, deploy scripts (`--require-hashes`) |
| **F-07 Ingress** | `api/ingress.py`, `api/app.py`, `api/routes/chat.py`, `brain_bus.py`, `api/telegram.py`, `agent/db.py`, `telegram_validator.py`, `brain_bus.py`, `tests/test_ingress_hardening.py` + related test fixes |
| **Env docs** | `.env.example` (SSH pin, callback allowlist, ingress vars) |
| **SoT** | `docs/ops/JADZIA-CORE-AUDIT-2026-07-21.md`, audit handoffs `2026-07-21-*`, `docs/handoffs/README.md`, `todo.json` |
| **Test drift** | `agent/design_agent_service.py`, design-agent + telegram/webhook test updates (full-suite green) |

### Park (poza tym PR)

- `deployment/mkt-dash01-verify.sh`
- `docs/handoffs/2026-07-19-SESSION-CLOSE-MKT-DASH.md`

### Szlify deploy-ready (2026-07-21 wieczór)

| Poprawka | Plik |
|----------|------|
| Mypy 0 errors na nowych modułach | `api/ingress.py`, `core/webhook_url_guard.py` |
| Deploy `--require-hashes` na hashed lock | `deployment/deploy-to-vps.sh`, `vps-deploy-closure.sh`, `.agents/workflows/jadzia-deploy.md` |
| Kontrakt: `uv.lock` trackowany | `tests/test_dependency_lock_contract.py`, `.gitignore` `!uv.lock` |
| Black scoped | 10 plików remediacji |

### Naprawione wcześniej (prep)

- `.gitignore`: dodano `!uv.lock` — bez tego CI `uv sync --locked` / `uv lock --check` pada po checkout
- Black na 10 plikach remediacji (scoped lint PASS)

## Plan commitów (1 PR, 6 commitów)

```text
1. ci: blocking full pytest + coverage artifact + gitleaks job (F-01)
2. quality: realistic jadzia-test workflow contract (F-11)
3. security: SSRF callback guard + redacted logs (F-02)
4. security: SSH host policy + safe archive extraction (F-03/F-09)
5. deps: uv.lock + hashed requirements.lock, Chroma removed (F-05)
6. ingress: widget/Telegram/Brain Bus hardening + audit docs/handoffs (F-07 + SoT)
```

**Branch:** `feat/audit-remediation-wave1-2`  
**PR title:** `fix(audit): Wave1–2 remediation — CI, SSRF, SSH, deps, ingress`  
**Merge:** squash optional; prefer merge commit for audyt trail.

## Pre-push gate (2026-07-21 — deploy-ready re-run)

| Gate | Command | Result |
|------|---------|--------|
| Full pytest | `uv run --locked python -m pytest tests/ -q` | **644 passed**, 17 skipped, 1 xfailed (104.5 s) |
| Contract tests | CI/quality/deps/ingress contracts | **17 passed** |
| Commander smoke | `TestCommanderUiSmoke` | **PASS** |
| Scoped mypy | new ingress/callback/ssh modules | **0 errors** |
| Lock check | `uv lock --check` | **PASS** (156 packages) |
| pip-audit | `pip-audit --strict -r requirements.lock` | **No known vulnerabilities** |
| Scoped lint | ruff + black on CI scope + contracts | **PASS** |
| GitHub Actions | — | **unverified** (nothing pushed) |
| VPS / deploy | — | **not started** |

## Commit + push — czeka na GO Dowódcy

**Nie wykonano:** commit, push, PR, deploy.

Po GO wykonać:

```powershell
git checkout -b feat/audit-remediation-wave1-2
# stage per commit plan above (exclude park files + noise)
git push -u origin feat/audit-remediation-wave1-2
gh pr create --title "fix(audit): Wave1–2 remediation — CI, SSRF, SSH, deps, ingress" ...
```

Po push: sprawdzić Actions (lint → test → security → secrets → typecheck). Jeśli red z tego batcha — naprawić przed merge.

### Org secret (przed pierwszym CI run)

Jeśli repo należy do org GitHub: dodać `GITLEAKS_LICENSE` w repo secrets (job `secrets` w `ci.yml`).

## Deploy plan — Zasada 11 (VPS dopiero po świeżym GO)

**standing_go_closeout:** `false` · **production:** UNVERIFIED

### Pre-deploy env checklist (VPS `.env`)

| Var | Akcja |
|-----|-------|
| `TELEGRAM_WEBHOOK_SECRET` | Ustawić; native webhook **musi** wysyłać `X-Telegram-Bot-Api-Secret-Token` |
| `WIDGET_CHAT_RATE_LIMIT` | Domyślnie 30/h; dostosować jeśli potrzeba |
| `PUBLIC_API_DOCS_ENABLED` | **0** (lub nie ustawiać) — `/docs` off na prod |
| `WEBHOOK_CALLBACK_ALLOWLIST` | HTTPS hosty callbacków workera |
| `SSH_KNOWN_HOSTS_PATH` / `SSH_HOST_KEY_FINGERPRINT` | **HITL** — pinning przed pierwszym SSH write po deploy |
| `INGRESS_RATE_SALT` | Losowy salt dla rate-limit hash (prod) |
| `GITLEAKS_LICENSE` | Tylko GitHub org secret (nie VPS) |

### Frontend (zzpackage) — blocker deploy ingress

Widget **musi** zapisywać `session_id` zwrócony przez `POST /api/v1/widget/chat` i wysyłać go w kolejnych requestach. Bez tego server-minted sessions nie działają.

### VPS deploy sequence (po świeżym GO)

1. Backup DB + `.env` na VPS
2. `git pull` / deploy script na `/opt/jadzia` — **bez** upload lokalnej DB
3. `uv pip install --require-hashes -r requirements.lock` (lub istniejący deploy script)
4. `systemctl restart jadzia` — jeden proces (single-process invariant)
5. Read-only smoke: OpenAPI 404, `/status`, widget chat z session continuity, Telegram secret reject
6. SSH: zweryfikować known_hosts/fingerprint przed write path
7. Evidence do aneksu audytu — dopiero wtedy `UNVERIFIED` → PASS/FAIL

### Nie wdrażać w tym batchu

- `AUD-REM-WRITE-01` (F-04 atomic multi-file)
- `AUD-REM-HEALTH-01` (F-06 metrics)
- `AUD-REM-DB-01` (F-08 SQLite WAL)
- Gate D, Mollie LIVE, merge OS↔jadzia

## Residual / next

| Task | Priorytet |
|------|-----------|
| Dowódca GO → commit/push/PR/Actions | **critical** |
| Widget frontend `session_id` | **critical** (przed prod ingress) |
| `AUD-REM-WRITE-01` | critical (F-04) |
| `AUD-REM-HEALTH-01`, `AUD-REM-DB-01`, `AUD-REM-OPS-01`, `AUD-REM-SOT-01` | high |
| Handoffs archive (29 > 15 policy) | `AUD-REM-SOT-01` |

## Start prompt (po GO)

```text
@vibe-init TASK_ID: AUD-REM-GIT-DEPLOY-PUSH
GO commit/push potwierdzony. Branch feat/audit-remediation-wave1-2,
6 commitów wg handoff 2026-07-21-AUD-REM-GIT-DEPLOY-01-CLOSE.md.
Po push: Actions green, potem ready_for_human na VPS GO.
```
