---
status: ACCEPTED (tool-side) · 2026-08-03 · MASTER-TODO-8 8-04
scope: tool-only — worker NIGDY nie dispatchuje live_gated ról (marketing PARKED)
---

# Agents Worker Loop — design (per-role cadence, jeden timer)

## Problem

Registry roles to orchestration shells: działają tylko gdy człowiek odpali
`hub agents run`. Heartbeat (7-02) udowodnił, że bez automatyzacji mechanizm
umiera. TARGET v5 §J zakłada cadence per rola — potrzebny scheduler.

## Decyzja: jeden timer + due-dispatcher (NIE 9 timerów, NIE in-process)

**Model:** `demand-os-agents-loop.timer` (co 15 min) → oneshot service →
`tools/demand_os_agents.py run-due --apply` → `agents.worker.run_due()`.

| Opcja | Werdykt |
|-------|---------|
| systemd timer per rola (9×) | Odrzucone — 18 plików unit, drift konfiguracji; K13 pokazał koszt jednego |
| In-process scheduler w `api/app.py` worker_loop | Odrzucone — miesza runtime aplikacji z ops cadence; restart = utrata stanu |
| **1 timer + due-dispatcher** | **Wybrane** — stan = heartbeat (już istnieje), konfiguracja = statyczna mapa w kodzie (reviewable), self-scheduling |

## Due logic

`due = heartbeat.last_run_at starszy niż cadence_hours LUB brak rekordu`.
Dispatcher iteruje statyczną mapę cadence i dispatchuje przez
`registry.dispatch` (auto-heartbeat 7-02 zapisuje run — pętla się domyka).

## Cadence map (tool-side only)

| Rola | Akcje | Cadence | Uzasadnienie |
|------|-------|---------|--------------|
| growth_lead | sync_starts, money_check | 24h | Money Check dziennik |
| sales | sync_hot, list_hot | 6h | STL zero overnight → 4×/dzień |
| validator | compliance | 24h | FAIL-rate watch |
| icp_brain | sync_memory | 24h | MEMORY z ops_bus świeże |
| cre | status | 24h | hot→wizard deeplink watch |
| tt, cf, fb, blog | — | **nigdy** | `live_gated=True` — worker poza zakresem (PARKED) |

## Reguły bezpieczeństwa

1. **Worker = tool-only na zawsze.** `live_gated` role są pomijane nawet po
   unlock (live cadence = decyzja HITL, nie schedulera).
2. **RBAC:** `run-due` wymaga `DEMAND_OS_ROLE=act` (service env); CLI dry-run domyślnie.
3. **Idempotencja:** wybrane akcje to read/upsert (sync/compliance/status) —
   powtórka nie szkodzi; brak publish/engage.
4. **Timer DISABLED by default** (jak K13: brak `[Install] WantedBy`) — enable
   dopiero `systemctl enable --now` po GO Dowódcy.
5. **Fail-closed:** każdy dispatch ma honest envelope; błąd jednej roli nie
   przerywa pętli (per-action try w `registry.dispatch`).

## `shell:false` criteria (odłożone, mechaniczne)

Rola traci marker `shell` gdy: worker dispatchuje ją ≥7 kolejnych dni bez
błędu envelope **oraz** wszystkie jej akcje mają testy kontraktowe. Dziś:
`shell: True` zostaje — worker najpierw musi udowodnić cadence w runtime.

## Artefakty

- `agent/demand_os/agents/worker.py` — cadence map + due + run_due
- `tools/demand_os_agents.py` — subcommand-style `run-due [--apply]`
- `deployment/demand-os-agents-loop.{service,timer}` — disabled by default
- `tests/unit/test_agents_worker.py` — due logic, live_gated skip, dry/apply
