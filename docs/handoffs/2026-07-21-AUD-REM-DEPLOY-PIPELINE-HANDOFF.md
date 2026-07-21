# Handoff — AUD-REM DEPLOY PIPELINE (next session owns full ship+test)

**Date:** 2026-07-21  
**Session close:** Wave1–4 code DONE · VPS **NOT** deployed  
**Task for next agent:** `AUD-REM-DEPLOY-PIPELINE-01`  
**standing_go_closeout:** `false` — VPS tylko po jawnym **GO** Dowódcy w tej sesji

## Stan git / PR

| Artefakt | Stan |
|----------|------|
| `master` Wave1–2 | **MERGED** PR #9 @ `da46c49` · Actions **green** |
| Wave3–4 | PR **#10** OPEN · tip `1d39379` · Actions **all SUCCESS** · MERGEABLE |
| Widget FE | flexgrafik-nl PR **#3** `feat/widget-session-id-adopt` — adopt server `session_id` |
| Lokalny branch | `feat/aud-rem-wave3-4` @ `1d39379` (synced origin) |
| Noise (nie commitować) | `.coverage`, `coverage.xml`, `.cursor/session-state.md` |
| Park | `deployment/mkt-dash01-verify.sh` |

## Co jest już zrobione (nie powtarzaj)

- F-01 CI, F-02 SSRF, F-03/F-09 SSH, F-05 deps, F-07 ingress, F-11 quality → na `master`
- F-04 WRITE, F-06 HEALTH, F-08 DB, F-10 PRIVACY, F-12 OPS docs, F-13 SoT → w PR #10
- Lokalny pytest Wave3–4: **649 passed**, 17 skipped, 1 xfailed
- Pack VPS: `docs/handoffs/2026-07-21-AUD-REM-VPS-READY.md`
- SLO/DR: `docs/ops/SLO-DR-RUNBOOK.md`

## Co zostaje — KOMPLEKSOWY PIPELINE DEPLOY (1 sesja)

Kolejność obowiązkowa (jedna ścieżka):

1. **Merge PR #10** (jadzia Wave3–4) — po zielonym CI (już green).
2. **Merge PR #3** (flexgrafik-nl widget session_id) + deploy theme na prod WP jeśli to Wasz flow.
3. **Fresh GO Dowódcy** na VPS (bez GO = STOP).
4. **Env HITL** na `/opt/jadzia/.env` wg checklisty poniżej.
5. **Deploy** hashed lock + restart **single process** (komendy w VPS-READY).
6. **Test narzędzia end-to-end** (nie tylko curl health):
   - OpenAPI `/docs` → **404**
   - `/worker/health` → 200, proces 1×
   - Widget chat (flexgrafik.nl): 2 wiadomości → ten sam `session_id` z odpowiedzi API
   - Telegram native: zły/brak secret → reject; dobry secret → update claim
   - SSH: known_hosts/fingerprint ustawione zanim write path
   - `PRAGMA journal_mode` → **wal**; `integrity_check` → ok
   - Opcjonalnie: dry dry-run approval path / Commander smoke jeśli dostępne bez Gate D/Mollie
7. **Evidence aneks** → aktualizacja audytu: production UNVERIFIED → PASS/FAIL.
8. Tip sync docs (`todo.json`, handoff close).

## Env checklist (VPS)

| Var | Wymaganie |
|-----|-----------|
| `TELEGRAM_WEBHOOK_SECRET` | native `X-Telegram-Bot-Api-Secret-Token` |
| `PUBLIC_API_DOCS_ENABLED` | `0` |
| `INGRESS_RATE_SALT` | losowy |
| `WIDGET_CHAT_RATE_LIMIT` | opcjonalnie 30 |
| `WEBHOOK_CALLBACK_ALLOWLIST` | HTTPS hosty |
| `SSH_KNOWN_HOSTS_PATH` / `SSH_HOST_KEY_FINGERPRINT` | HITL |
| `WP_HEALTH_CHECK_URL` / `SHOP_URL` | health target |

Install: `pip install --require-hashes -r requirements.lock`  
**Nie** uploaduj lokalnej DB (deploy default = N).

## Hard STOP

- Autonomiczny deploy bez GO · sekrety w git · force-push · Gate D · Mollie LIVE · fake PASS
- Multi-worker uvicorn (psuje schedulery + SQLite)

## Start prompt (wklej w nową sesję)

```text
@vibe-init
TASK_ID: AUD-REM-DEPLOY-PIPELINE-01
Cel: KOMPLEKSOWY pipeline — merge PR#10 + flexgrafik-nl PR#3, potem po jawnym GO
Dowódcy pełny deploy VPS Wave1–4 + E2E test narzędzia (widget session_id,
Telegram secret, health, WAL, OpenAPI 404). Evidence → audyt PASS/FAIL.

Przeczytaj:
1. docs/handoffs/2026-07-21-AUD-REM-DEPLOY-PIPELINE-HANDOFF.md
2. docs/handoffs/2026-07-21-AUD-REM-VPS-READY.md
3. docs/ops/SLO-DR-RUNBOOK.md
4. todo.json (AUD-REM-VPS-VERIFY-01)

Kolejność: merge → GO → env HITL → deploy hashed lock → smoke+E2E → aneks.
Hard STOP bez GO. standing_go_closeout=false. Kończ @handoff.
```

## Definition of Done następnej sesji

- [ ] PR #10 i PR #3 merged
- [ ] VPS tip = master tip po Wave3–4
- [ ] E2E checklist powyżej z timestamp/exit codes
- [ ] `AUD-REM-VPS-VERIFY-01` completed lub FAIL z residual
- [ ] Produkcją nie oznaczona PASS bez evidence
