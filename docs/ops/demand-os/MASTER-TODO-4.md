---
gate: DEMAND-OS-MARKETING-4-00
status: ACTIVE · prep · awaiting GO
updated: "2026-08-03"
owner: agent-orchestrator
human_gate: "Founder GO MARKETING HITL"
prerequisite: "Etap 5f SEALED · Hard DoD 15/15"
close_target: "marketing_hitl_gate READY · first HITL publish logged"
---

# MASTER TODO — Etap 4 (Marketing HITL live)

> **Jedyny aktywny backlog po 5f SEAL.** Marketing **nie** startuje bez Founder `GO MARKETING HITL`.  
> Domykaj: **PREP → GO ceremony → P0 first publish → SEAL**.

## Hierarchia SoT

| Priorytet | Plik | Rola |
|-----------|------|------|
| 1 | **Ten plik** | Co robić teraz |
| 2 | [`GO-MARKETING-HITL-CHECKLIST.md`](./GO-MARKETING-HITL-CHECKLIST.md) | Ceremonia GO (human) |
| 3 | [`STATE.md`](./STATE.md) | Faza · prod_tip |
| 4 | [`.cursor/current-task.md`](../../../.cursor/current-task.md) | Jedno aktywne zadanie |
| 5 | [`ORGANIC-AGENCY-SPRINT-14D.md`](./ORGANIC-AGENCY-SPRINT-14D.md) | Rytm 14d organic |
| 6 | [`HITL-READY-TOOL.md`](./HITL-READY-TOOL.md) | DoD maszyny dry |

## Stan wejścia (post 5f SEAL 2026-08-03)

| Pole | Wartość |
|------|---------|
| 5f | SEALED · Hard DoD 15/15 |
| prod | `5713cbc` · cache `desk-dash08` |
| go_day_ready | **100%** (tool side) |
| marketing_hitl_gate | **BLOCKED** (default) |
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
| **4-GO-01** | Founder **`GO MARKETING HITL`** | Dowódca | `ready_for_human` | wpis w handoff + data |
| **4-GO-02** | VPS env `DEMAND_OS_MARKETING_HITL=GO` | Ops | `open` | po GO-01 · restart jadzia |
| **4-GO-03** | Verify prod gate READY | Agent | `open` | status API · Desk banner |

### P0 — first HITL actions (post-GO)

| ID | Zadanie | Owner | Status | DoD |
|----|---------|-------|--------|-----|
| **4-P0-01** | TT publish `tt_w32_install_01` HITL | Dowódca+Agent | `open` | Val PASS · ledger row · no dry |
| **4-P0-02** | FB hunt dry→live comment #1 | Dowódca | `open` | ENGAGE-LOG · allowlist |
| **4-P0-03** | Blog ship `blog_w31_install_bus50m` | Dowódca | `open` | BLOG-HITL-SHIP checklist |

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
CURRENT: 4-GO-01 (Founder GO MARKETING HITL)
NEXT:    4-GO-02 VPS env → 4-GO-03 verify → 4-P0-01 TT publish
BLOCKED: live publish until GO-01
```

## Verify (agent — każda sesja)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_hub.py doctor
python -c "from agent.demand_os.week_ritual import go_day_ready; print(go_day_ready())"
python -m pytest tests/test_demand_os_marketing_mode.py tests/test_demand_os_desk_contract.py -q
```

## STOP

- Live publish bez GO
- Ads / boost / € spend
- VPS deploy bez GO
- Auto-publish Wave3
- Fałszywy SEAL bez REAL ledger

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
