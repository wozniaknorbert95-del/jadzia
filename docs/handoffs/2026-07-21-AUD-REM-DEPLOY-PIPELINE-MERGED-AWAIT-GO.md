# Handoff — AUD-REM DEPLOY PIPELINE (MERGED · AWAIT GO)

**Date:** 2026-07-21  
**Task:** `AUD-REM-DEPLOY-PIPELINE-01`  
**standing_go_closeout:** `false`  
**Status:** code MERGED · VPS **NOT** deployed · production **UNVERIFIED**

## DONE this session

| Artefakt | Wynik |
|----------|--------|
| jadzia PR **#10** | **MERGED** → `master` tip **`3604f60`** (merge of `1d39379`) |
| CI before merge | lint/test/typecheck/security/secrets — all **SUCCESS** |
| flexgrafik-nl PR **#3** | **MERGED** → `main` tip **`a5cfa36`** |
| VPS deploy | **STOP** — no GO in this session |
| E2E / audyt PASS | **NOT** run — requires deploy evidence |

## LEFT (kolejność po GO)

1. **Fresh GO Dowódcy** (wklej dokładnie):
   ```text
   GO VPS deploy+verify AUD-REM-VPS-VERIFY-01 tip 3604f60
   ```
2. **Env HITL** `/opt/jadzia/.env` — checklist w `docs/handoffs/2026-07-21-AUD-REM-VPS-READY.md`
3. **WP theme deploy** flexgrafik-nl `@a5cfa36` (widget `session_id` adopt) — Wasz flow HITL
4. **Deploy** hashed lock + single-process restart (komendy w VPS-READY)
5. **Smoke + E2E:** `/docs`→404 · health 200 · process=1 · WAL · widget 2 msg same session_id · Telegram secret reject/accept
6. **Aneks** → `docs/ops/JADZIA-CORE-AUDIT-2026-07-21.md` production UNVERIFIED → PASS/FAIL

## Hard STOP

- Autonomiczny deploy bez GO · sekrety · force-push · Gate D · Mollie LIVE · fake PASS · multi-worker

## Start prompt (po GO)

```text
@vibe-init
TASK_ID: AUD-REM-DEPLOY-PIPELINE-01
GO VPS deploy+verify AUD-REM-VPS-VERIFY-01 tip 3604f60
Cel: env HITL → deploy hashed lock → smoke+E2E → aneks audytu PASS/FAIL.
Pack: docs/handoffs/2026-07-21-AUD-REM-VPS-READY.md + docs/ops/SLO-DR-RUNBOOK.md
standing_go_closeout=false już spełnione przez GO powyżej. Kończ @handoff.
```

## Definition of Done (nadal otwarte)

- [x] PR #10 i PR #3 merged
- [ ] VPS tip = `3604f60`
- [ ] E2E checklist z timestamp/exit codes
- [ ] `AUD-REM-VPS-VERIFY-01` completed lub FAIL z residual
- [ ] Produkcją nie oznaczona PASS bez evidence
