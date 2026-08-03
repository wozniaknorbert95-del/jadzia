---
gate: DEMAND-OS-MARKETING-4-00
status: ACTIVE · TOOL 100% SEALED · live P0 PARKED
updated: "2026-08-03"
owner: agent-orchestrator
human_gate: "Dowódca unlock live marketing (separate ceremony)"
prerequisite: "Etap 5f SEALED · Hard DoD 15/15 · GO LIVE done · TOOL 100% SEAL"
close_target: "awaiting Dowódca unlock for live 4-P0-*"
---

# MASTER TODO — Etap 4 (Marketing HITL · TOOL FIRST)

> **Kierunek Dowódcy (2026-08-03):** najpierw **narzędzie 100%**.  
> Jakiekolwiek publikacje **tylko testowo** (proof → delete). Live `4-P0-*` PARKED.  
> Rule: [`.cursor/rules/demand-os-tool-first.mdc`](../../../.cursor/rules/demand-os-tool-first.mdc)

## Hierarchia SoT

| Priorytet | Plik | Rola |
|-----------|------|------|
| 1 | **Ten plik** | Co robić teraz |
| 2 | [`GO-MARKETING-HITL-CHECKLIST.md`](./GO-MARKETING-HITL-CHECKLIST.md) | Ceremonia GO (human) |
| 3 | [`STATE.md`](./STATE.md) | Faza · prod_tip |
| 4 | [`.cursor/current-task.md`](../../../.cursor/current-task.md) | Jedno aktywne zadanie |
| 5 | [`P0-HITL-PREFLIGHT.md`](./P0-HITL-PREFLIGHT.md) | Pakiet wejścia do P0 |
| 6 | [`4-P0-01-TT-HITL-EXECUTION-PACKET.md`](./4-P0-01-TT-HITL-EXECUTION-PACKET.md) | Packet operatora TT |
| 7 | [`ORGANIC-AGENCY-SPRINT-14D.md`](./ORGANIC-AGENCY-SPRINT-14D.md) | Rytm 14d organic |
| 8 | [`HITL-READY-TOOL.md`](./HITL-READY-TOOL.md) | DoD maszyny dry |

## Stan wejścia (post 5f SEAL 2026-08-03)

| Pole | Wartość |
|------|---------|
| 5f | SEALED · Hard DoD 15/15 |
| prod | `2f68b64` · gate READY · `5713cbc` desk-dash08 UI close |
| go_day_ready | artifact score (≠ Tool SEAL) |
| marketing_hitl_gate | env-dependent · live cadence **PARKED** |
| GO switch | `DEMAND_OS_MARKETING_HITL=GO` on VPS (env-only) |
| Ads | **PARK cash** · €0 spend |

## MASTER BACKLOG

Legenda: `open` · `in_progress` · `done` · `blocked` · `ready_for_human`

### PREP — agent (done before GO)

| ID | Zadanie | Status | DoD |
|----|---------|--------|-----|
| **4-PREP-01** | `marketing_mode.py` env switch | `done` | default PARKED · GO→READY |
| **4-PREP-02** | MASTER-TODO-4 + GO checklist | `done` | ten plik + checklist |
| **4-PREP-03** | doctor/go_day verify | `done` | go_day 100% · handoff |

### GO — human ceremony

| ID | Zadanie | Owner | Status | DoD |
|----|---------|-------|--------|-----|
| **4-GO-01** | Founder **`GO MARKETING HITL`** | Dowódca | `done` | `2026-08-03-GO-MARKETING-HITL.md` |
| **4-GO-02** | VPS deploy `2f68b64` + env GO | Ops | `done` | EXEC-CLOSE handoff |
| **4-GO-03** | Verify prod gate READY | Agent | `done` | VPS + browser prod |

### TOOL — active now (before any live publish)

| ID | Zadanie | Owner | Status | DoD |
|----|---------|-------|--------|-----|
| **4-TOOL-01** | Demand OS tool 100% residual | Agent | `done` | doctor tip TOOL_FIRST · footer honesty · waves mode · connectors · verify pack |
| **4-TOOL-02** | Test publish only if tool needs proof | Agent | `done` | dry gate path + [`4-TOOL-02-TEST-PUBLISH.md`](./4-TOOL-02-TEST-PUBLISH.md) · no live SEAL |

### P0 — live HITL (PARKED until tool 100% + Dowódca unlock)

| ID | Zadanie | Owner | Status | DoD |
|----|---------|-------|--------|-----|
| **4-P0-01** | TT publish `tt_w32_install_01` HITL | Dowódca+Agent | `blocked` | PARKED · not next |
| **4-P0-02** | FB hunt dry→live comment #1 | Dowódca | `blocked` | PARKED |
| **4-P0-03** | Blog ship `blog_w31_install_bus50m` | Dowódca | `blocked` | PARKED |

### P1 — rhythm (week 1 post-GO)

| ID | Zadanie | Status | DoD |
|----|---------|--------|-----|
| **4-P1-01** | TT ≥3/wk Val→publish | open | calendar validated slots |
| **4-P1-02** | FB hunt 1/dzień roboczy | open | FB-HUNT-DAILY |
| **4-P1-03** | Ledger daily | open | LEDGER.csv |
| **4-P1-04** | Money Check Pon | open | week ritual |

### P2 — SEAL Etap 4

| ID | Zadanie | Status | DoD |
|----|---------|--------|-----|
| **4-P2-01** | ≥1 REAL publish each channel | open | TT + blog + hunt evidence |
| **4-P2-02** | STATE + handoff CLOSE | open | `DEMAND-MARKETING-4-CLOSE.md` |

## Aktywne zadanie (pointer)

```
CURRENT: 4-TOOL-100 SEAL (tool residual closed)
NEXT:    awaiting Dowódca unlock for live 4-P0-* (not auto)
BLOCKED: live 4-P0-01/02/03 until explicit Dowódca unlock
```

## Verify (agent — każda sesja)

Canonical pack: [`OWNER-VERIFY-COMMANDS.md`](./OWNER-VERIFY-COMMANDS.md)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -m pytest tests/test_demand_os_tool_first_pointer.py -q
python -m pytest tests -k demand_os -q
```

Note: `go_day_ready` score = artifact metric, **not** Tool 100% SEAL.

## STOP

- Live publish jako „następny krok” przed tool 100%
- Ads / boost / € spend
- VPS deploy bez GO
- Auto-publish Wave3
- Fałszywy SEAL / fake ledger `publish=Y`
- Handoffy typu „Founder publish now” — **stale** dopóki brak unlock

## GO execution (po Founder GO)

```bash
# VPS — tylko po GO MARKETING HITL
echo 'DEMAND_OS_MARKETING_HITL=GO' >> /opt/jadzia/.env
systemctl restart jadzia
curl -s -H "Authorization: Bearer $JWT" …/api/v1/commander/demand-os/status | jq .diagnostics.marketing_hitl_gate
# expect: "READY"
```

Rollback: usuń env var · restart · gate wraca BLOCKED.

---

*v4 MASTER · Etap 4 · GO-gated · zero ściemy*
