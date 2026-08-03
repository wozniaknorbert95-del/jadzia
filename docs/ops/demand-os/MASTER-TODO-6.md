---
gate: DEMAND-OS-AGENTS-6-00
status: ACTIVE
updated: "2026-08-03"
owner: agent-orchestrator
supersedes_gate: DEMAND-OS-DESK-5F-00 (SEALED — nie cofać)
close_target: "agents tool 100% per TARGET v5 §E/§H/§J — done means code + tests + evidence"
coverage_map: "docs/ops/demand-os/OS-TARGET-V5-AGENTS-COVERAGE.md"
---

# MASTER TODO — Etap 6 (Agents tool 100% · TARGET v5)

> **Zakres: tool-only.** Marketing live (publish/reply/outbound/Ads) = PARKED do `UNLOCK-LIVE-P0.md`.
> Jedno zadanie = jeden deliverable + testy. Zero zgadywania — każdy item ma źródło GAP.

## Hierarchia SoT

1. Ten plik (agents backlog) · 2. `STATE.md` · 3. `.cursor/current-task.md` · 4. `todo.json` (`active_item` = `4-TOOL-AGENTS-6-*`) · 5. `OS-TARGET-V5-AGENTS-COVERAGE.md`

**Zakaz:** live publish · fake `shell:false` bez worker loop · nowy etap bez CLOSE · commit `set-now/` secrets.

## Definition of Done (per item)

- [ ] Kod + testy jednostkowe (nowe lub rozszerzone) — zielone
- [ ] `python tools/commander_release.py validate` ok
- [ ] Evidence w handoffie / coverage map sync
- [ ] Uczciwy status: blocked human-only = jawnie, nie „done”

## Backlog (10)

| ID | Zadanie | GAP źródło | Status | Verify |
|----|---------|-----------|--------|--------|
| **6-01** | SoT sync: STATE/todo/pointer tips | STATE miał prod_tip 4093179 desk-dash09 vs real 74683e2 desk-dash11 | `done` | pointer tests |
| **6-02** | Ten plik — gate + backlog | brak kanonicznego backlog agents | `done` | — |
| **6-03** | Heartbeat per rola → last_run w `list_agents` | registry bez historii = zawsze `shell:true` | `done` | `test_agents_heartbeat.py` (7) |
| **6-04** | owner-verify += wave-check + registry contract | tool 100% nie egzekwowane w jednym gate | `done` | owner-verify exit 0 (7 kroków) |
| **6-05** | Coverage gate += `agents.registry/flow/wave_check` ≥80% | k12 gate nie obejmuje agents | `done` | total 92%, min moduł 82% — `k12-coverage-agents.txt/json` |
| **6-06** | `agents flow --apply` → bind calendar slot | §E chain kończy się przed calendar MCP | `done` | slot validated + pass_token, idempotent re-bind |
| **6-07** | `agents flow` += fatigue check (B.4) | B.4 wymaga fatigue przed publish | `done` | soft warn, chain proceeds (tests fresh+tired) |
| **6-08** | wave-check W4: real episodic + fatigue checks | W4 check = tylko „layer present” | `done` | episodic keys + fatigue probe + a2a bus file |
| **6-09** | GA4 inline JSON contract test + docs | credentials path = jedyne live unblock bez pliku | `done` | path/garbage inline ≠ live (test) |
| **6-10** | Desk tile „Agenci” + `desk-dash12` | desk nie pokazuje rejestru agentów | `done` | UI contract `test_desk_agents_tile_contract` |

**Bugfix w trakcie:** zagnieżdżony `if wave == 4` w `wave_check.py` (W4 checks nigdy się nie wykonywały) — naprawiony + regression test.

## Po backlogu (NEXT, nie teraz)

- Worker loop per rola → `shell: false` (wymaga scheduler design, osobny gate)
- GDrive real connector (Drive list client) — `not_wired` dopóki brak klienta
- Live P0 — PARKED

## Verify gate (każda sesja)

```bash
python tools/demand_os_hub.py agents wave-check
python -m pytest tests/unit/test_agents_registry.py tests/unit/test_agents_flow_wave.py -q
python tools/commander_release.py validate
```

## STOP (hard)

- Live publish / social connectors / Ads
- `shell:false` bez worker loop
- Fake live PASS w wave-check (live = human cadence, zawsze ręczne)
