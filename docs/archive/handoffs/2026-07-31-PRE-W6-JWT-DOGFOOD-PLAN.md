---
status: "[SUPERSEDED-BY-CLOSE]"
close: "docs/handoffs/2026-07-31-PRE-W6-JWT-DOGFOOD-CLOSE.md"
title: "PRE-W6 — JWT prod dogfood + SoT hygiene (before W6 GO)"
updated: "2026-07-31"
gate: "PRE-W6-JWT-DOGFOOD"
depends_on: "VF-VHQ-W5-OPERATIONS-BUS DEPLOY LIVE"
prod_url: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w50a"
prod_tip: "94268f7"
runtime: "174603e"
cache: "vhq-w50a"
w6_start: false
---

# PRE-W6 Plan — JWT prod dogfood + SoT hygiene

## Goal

Zamknąć residual **G4** (prod UI bus trail wymaga JWT) + drobny tip-drift SoT **zanim** GO na `VF-VHQ-W6-DIRECTOR-APPROVALS`.

**Decision (locked):** jedna ścieżka = Founder JWT dogfood na LIVE W5 + tip hygiene.  
**Nie startujemy W6.** Nie ruszamy Order LIVE / Ads / Mollie / MKT / pełnego katalogu §8.

## Why before W6

W6 = Approval Vault (L2–L4). Bazuje na Ops Bus. API LIVE jest; UI trail bez JWT jest ślepy. Dogfood JWT daje dowód, że spine cash jest widoczny Directorowi przed budową approve UX.

## In / Out

### In
- Prod JWT session `?v=vhq-w50a`
- Sales ack → Wizard bus cards (`lead_qualified` / `wizard_started`)
- Order PARKED · EV-W2-010
- Optional tip-drift grep (scorecard / AGENTS / program leftover `vhq-w40c`)
- Evidence + stamp handoff · todo/current-task update

### Out / STOP
- W6 implement
- Order Desk LIVE
- Silent L3/L4
- Ads / Mollie / Gate D
- Commit `docs/ops/marketing/**`
- Deploy bez potrzeby (docs-only tip sync OK jeśli hygiene)

## Parallel agent map

| Agent | Domain | Deliverable |
|-------|--------|-------------|
| A — Prod JWT dogfood | UI + API on VPS/prod | checklist PASS + screenshots |
| B — SoT tip drift | docs grep `vhq-w40c` / `6375ab1` stale | patch list or apply docs-only |
| C — Hygiene gate | git dirty MKT / allowlist | confirm MKT unstaged |

## Binary DoD

| ID | Claim |
|----|-------|
| D1 | JWT on prod Commander `vhq-w50a` |
| D2 | Wizard shows Operations Bus typed cards (or last-bus on MC) |
| D3 | Order Desk PARKED · EV-W2-010 · no LIVE |
| D4 | Evidence dir + handoff stamped |
| D5 | MKT not staged |
| D6 | W6 remains parked · no GO invent |

## Sequence

1. Write this plan (done)
2. Parallel agents A+B+C
3. Parent synthesizes stamp handoff
4. Docs tip-sync commit **only if** B has real patches (no MKT)
5. STOP — await explicit **GO W6**

## Rollback

N/A (verify-only). Soft: clear JWT from browser; no schema changes.

PLAN_VERDICT: **SUPERSEDED BY CLOSE** — JWT dogfood PASS · SoT hygiene applied · W6 blocked until separate GO.
