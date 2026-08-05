# CURRENT TASK — AGENTS Etap 6 · live P0 PARKED

**Gate:** `DEMAND-OS-MARKETING-4-00` · agents backlog: `MASTER-TODO-8` DONE → `MASTER-TODO-9`  
**Prod tip:** `a892ce0` · cache `desk-dash13` · prod owner-verify **ok:true** · **worker timer LIVE** (15 min) · doctor staleness **blocking** na prod  
**Self-audit:** [`docs/handoffs/2026-08-05-PUNCH-LISTA-C-SELF-AUDIT.md`](../docs/handoffs/2026-08-05-PUNCH-LISTA-C-SELF-AUDIT.md) — 9 gapów (G1-G9) domkniętych + senior review (dangling links fixed)  
**Close:** [`docs/handoffs/2026-08-05-SELF-AUDIT-REVIEW-CLOSE.md`](../docs/handoffs/2026-08-05-SELF-AUDIT-REVIEW-CLOSE.md)  
**Next:** [`MASTER-TODO-9`](../docs/ops/demand-os/MASTER-TODO-9.md) kolumna **Kolejność** — 1: 9-01 (2026-08-12) · 2: 9-09 canary · 3: 9-02 desk chip limits  
**Verify:** `python tools/demand_os_owner_verify.py` · `hub agents wave-check` · `journalctl -u demand-os-agents-worker.service`  
**Human:** [`docs/ops/demand-os/UNLOCK-LIVE-P0.md`](../docs/ops/demand-os/UNLOCK-LIVE-P0.md)  
**Coverage:** [`docs/ops/demand-os/OS-TARGET-V5-AGENTS-COVERAGE.md`](../docs/ops/demand-os/OS-TARGET-V5-AGENTS-COVERAGE.md)  
**Register:** [`docs/ops/demand-os/AUDIT-K-REGISTER.md`](../docs/ops/demand-os/AUDIT-K-REGISTER.md)

## Status

- TOOL 100% = SEALED · OPS HARDENING = SEALED
- Punch lista C1–C8 = DONE (2026-08-05): **worker timer LIVE** na prod · D9-01 probe-heartbeat fix · D9-02 split-brain runtime path fix · stash 0 · gitignore secrets/output · suite zostawia czyste tree · doctor staleness alias · RBAC run-due test · E2E desk prod
- TARGET v5 pokrycie = W1–W4 `tool_ready` + worker (cadence roles `shell:false`)
- Live `4-P0-*` = PARKED until You sign unlock

## Teraz (Dowódca)

1. Desk: sekcja **Agenci Demand OS** — chip `dziś` + `bieg: 2026-08-05` (live, verified)
2. Obserwuj worker: `journalctl -u demand-os-agents-worker.service` (cykl 15 min)
3. Albo podpisz UNLOCK (handoff) — albo zostaw parked
4. Agent nie publikuje

## STOP

Live marketing · Ads · fake ledger · VPS git bez `sudo -u jadzia`
