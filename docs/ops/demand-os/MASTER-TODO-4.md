---
gate: DEMAND-OS-MARKETING-4-00
status: ACTIVE · OPS HARDENING · TOOL 100% SEALED · live P0 PARKED
updated: "2026-08-03"
owner: agent-orchestrator
human_gate: "UNLOCK-LIVE-P0.md (Dowódca only)"
prerequisite: "Etap 5f SEALED · TOOL 100% SEAL · OPS HARDENING · UX desk-dash09"
close_target: "Await UNLOCK-LIVE-P0 · then 4-P0-* HITL"
---

# MASTER TODO — Etap 4 (Marketing HITL · TOOL FIRST · OPS)

> **Kierunek:** tool 100% SEALED → **OPS HARDENING** → unlock tylko przez [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md).  
> Live `4-P0-*` PARKED. Rule: [`.cursor/rules/demand-os-tool-first.mdc`](../../../.cursor/rules/demand-os-tool-first.mdc)

## Hierarchia SoT

| Priorytet | Plik | Rola |
|-----------|------|------|
| 1 | **Ten plik** | Co robić teraz |
| 2 | [`GO-MARKETING-HITL-CHECKLIST.md`](./GO-MARKETING-HITL-CHECKLIST.md) | Ceremonia GO (human) |
| 3 | [`STATE.md`](./STATE.md) | Faza · prod_tip |
| 4 | [`.cursor/current-task.md`](../../../.cursor/current-task.md) | Jedno aktywne zadanie |
| 5 | [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md) | Ceremonia unlock cadence |
| 6 | [`OWNER-VERIFY-COMMANDS.md`](./OWNER-VERIFY-COMMANDS.md) | Verify pack |
| 7 | [`SYNC-SET-NOW.md`](./SYNC-SET-NOW.md) | Safe set-now sync |
| 8 | [`P0-HITL-PREFLIGHT.md`](./P0-HITL-PREFLIGHT.md) | Pakiet P0 (parked) |

## Stan wejścia (post TOOL-100 deploy)

| Pole | Wartość |
|------|---------|
| 5f | SEALED · Hard DoD 15/15 |
| prod runtime | **`1545415`** · cache **desk-dash09** · OPS floor `a3deb59` |
| go_day_ready | artifact score (≠ Tool/OPS SEAL) |
| marketing_hitl_gate | env may be READY · live cadence **PARKED** |
| GO switch | `DEMAND_OS_MARKETING_HITL=GO` on VPS (env ≠ unlock) |
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

### TOOL — sealed

| ID | Zadanie | Owner | Status | DoD |
|----|---------|-------|--------|-----|
| **4-TOOL-01** | Demand OS tool 100% residual | Agent | `done` | SEAL tip `889258e` → OPS `a3deb59` |
| **4-TOOL-02** | Test publish dry path | Agent | `done` | [`4-TOOL-02-TEST-PUBLISH.md`](./4-TOOL-02-TEST-PUBLISH.md) |

### OPS — hardening (sealed)

| ID | Zadanie | Owner | Status | DoD |
|----|---------|-------|--------|-----|
| **4-OPS-01** | SoT tip reconcile | Agent | `done` | no stale `2f68b64` in active pointers |
| **4-OPS-02** | Safe set-now sync | Agent | `done` | dry-run default · no `--delete` · runtime exclude |
| **4-OPS-03** | MEMORY write path | Agent | `done` | `DEMAND_OS_MEMORY` · log fallback |
| **4-OPS-04** | Owner verify script | Agent | `done` | `tools/demand_os_owner_verify.py` exit 0 |
| **4-OPS-05** | Pack coherence | Agent | `done` | sanitized README REQUIRED/OPTIONAL |
| **4-OPS-06** | Unlock ceremony doc | Agent | `done` | [`UNLOCK-LIVE-P0.md`](./UNLOCK-LIVE-P0.md) |
| **4-OPS-07** | Secondary pointer cleanup | Agent | `done` | no 4-TOOL-01 ACTIVE drift |
| **4-OPS-08** | Prod desk footer smoke | Agent | `done` | phone checklist Etap 4 + evidence |
| **4-OPS-09** | Money narrative cadence | Agent | `done` | `live_cadence=PARKED` |
| **4-OPS-10** | OPS HARDENING SEAL | Agent | `done` | SEAL handoff |
| **4-UNLOCK-PREP** | Unlock preflight (no publish) | Agent | `done` | preconditions checked · ready_for_human |

### P0 — live HITL (PARKED until UNLOCK-LIVE-P0)

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
CURRENT: 4-AWAIT-UNLOCK · ready_for_human · PARK leave recorded
NEXT:    Dowódca signs UNLOCK-LIVE-P0 (or keep parked)
BLOCKED: live 4-P0-01/02/03 until unlock handoff exists
HYGIENE: Post-TOOL N1–N7 CLOSE · tip 1545415 · desk-dash09
```

## Verify (agent — każda sesja)

```bash
export DEMAND_OS_SET_NOW=data/demand-os/set-now-sanitized
python tools/demand_os_owner_verify.py
```

Canonical detail: [`OWNER-VERIFY-COMMANDS.md`](./OWNER-VERIFY-COMMANDS.md)  
Note: `go_day_ready` score = artifact metric, **not** Tool/OPS SEAL.

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
