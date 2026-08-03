# CURRENT TASK — AGENTS Etap 6 · live P0 PARKED

**Gate:** `DEMAND-OS-MARKETING-4-00` · agents backlog: `MASTER-TODO-8` DONE → `MASTER-TODO-9`  
**Prod tip:** `ca86910` · cache `desk-dash13` · prod owner-verify **ok:true** · **maraton audit:** [`docs/handoffs/2026-08-03-MARATON-678-VERIFICATION-AUDIT.md`](../docs/handoffs/2026-08-03-MARATON-678-VERIFICATION-AUDIT.md) (punch lista C1-C8 = plan na jutro)  
**Verify:** `python tools/demand_os_owner_verify.py` · `hub agents wave-check` · `hub agents run-due`  
**Human:** [`docs/ops/demand-os/UNLOCK-LIVE-P0.md`](../docs/ops/demand-os/UNLOCK-LIVE-P0.md)  
**Agents handoff:** [`docs/handoffs/2026-08-03-DEMAND-OS-AGENTS-8-WORKER-HARDENING.md`](../docs/handoffs/2026-08-03-DEMAND-OS-AGENTS-8-WORKER-HARDENING.md)  
**Coverage:** [`docs/ops/demand-os/OS-TARGET-V5-AGENTS-COVERAGE.md`](../docs/ops/demand-os/OS-TARGET-V5-AGENTS-COVERAGE.md)  
**Register:** [`docs/ops/demand-os/AUDIT-K-REGISTER.md`](../docs/ops/demand-os/AUDIT-K-REGISTER.md)

## Status

- TOOL 100% = SEALED · OPS HARDENING = SEALED
- MASTER-TODO-6/7 = DONE (heartbeat, flow, writable-path prod contract, suita 688 green)
- MASTER-TODO-8 (10 zadań) = DONE: **worker loop** (`run-due`, tool-only) · staleness wave-check · 9 writerów probe · coverage gate agents ≥80% · desk staleness chip (`desk-dash13`) · SoT tip pointer · GDrive live client (fail-closed)
- TARGET v5 pokrycie = W1–W4 `tool_ready` + worker; live PASS = PARKED (human cadence)
- Live `4-P0-*` = PARKED until You sign unlock

## Teraz (Dowódca)

1. Desk po deploy: sekcja **Agenci Demand OS** — chip `dziś/Nd` (fresh/aging/stale)
2. Decyzja: aktywacja timera workera (`deployment/demand-os-agents-worker.timer`) — Zasada 11, Twój GO
3. Albo podpisz UNLOCK (handoff) — albo zostaw parked
4. Agent nie publikuje

## STOP

Live marketing · Ads · fake ledger · `shell:false` bez worker loop
