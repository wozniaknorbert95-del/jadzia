# Handoff — Demand OS Agents → Tool 100% (registry SoT)

**Date:** 2026-08-03
**Scope:** sekcja „Agenci” (Demand OS) — ze szkiców do profesjonalnego narzędzia
**Live P0:** PARKED (bez zmian)
**Cache:** `desk-dash11` (bez zmian — desk UI nietknięty)

## Problem

Wave1–3 shells były szkicami: trzy różne entrypoint (`run_agent` / `run_wave2` / `run_wave3`),
brak deklaratywnego rejestru, brak ujednoliconego envelope, CLI z kruchą logiką rozgałęzień,
brak testów kontraktu, zero ochrony RBAC dla mutujących akcji.

## Dostarczone

1. **`agent/demand_os/agents/registry.py`** — deklaratywny SoT dla 9 ról (wave 1–3):
   wave, label, kpi, actions, mutating_actions, live_gated, runner.
2. **Unified dispatch envelope** — `{ok, role, wave, action, result, raw, marketing, live_allowed, blocked_reason}`.
   Unknown role / disallowed action / runner exception → `ok=False` z jawnym błędem (nigdy crash, nigdy cisza).
3. **`list_agents()`** — projekcja rejestru z honesty markerami (`shell: true`, `live_allowed`, `blocked_reason` gdy PARKED).
4. **Hub `agents list|run`** — read-only przez RBAC; mutating actions jawnie kierowane do dedykowanych subcommands (`sync-db` / `sync-leads` / `memory-*`).
5. **`tools/demand_os_agents.py`** — refactor na registry; mutating = dry-run domyślnie, `--apply` wykonuje.
6. **Testy** — `tests/unit/test_agents_registry.py` (24): kontrakt rejestru, projekcja PARKED/GO, dispatch per-role smoke, hub CLI (list/wave-filter/run/mutating-block), legacy CLI dry-run default.

## Verify

```text
pytest test_agents_registry.py            → 24 passed
pytest tool100 + residual + coherence     → 50 passed
pytest commander api + sla regression     → 29 passed
python tools/commander_release.py validate → ok (62 passed, desk-dash11)
python tools/demand_os_hub.py agents list → 9 ról, honest live_allowed
```

## Granice (uczciwie)

- Shells ≠ autonomiczni agenci — to orkiestracja nad hub tools; `shell: true` zostaje w projekcji dopóki nie ma worker loop per rola.
- Live-gated role (`tt`, `cf`, `fb`, `blog`) raportują `live_allowed=false` dopóki marketing PARKED.
- Desk UI „Agenci” pokazuje ops registry (`agent/commander/agents_registry.py`) — nie ruszone (SEALED 5F).

## RECOMMENDED_NEXT

1. Desk tile „Demand OS Agenci” z `list_agents()` (osobny item, po GO na UI diff).
2. Worker loop per rola → dopiero wtedy `shell: false`.
3. Live P0 nadal PARKED do `UNLOCK-LIVE-P0.md`.
