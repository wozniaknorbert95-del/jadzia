---
status: "[ACTIVE]"
title: "Demand OS — execution state machine"
updated: "2026-08-01"
gate: "DEMAND-OS-SET-NOW-00"
last_step: "DOS-W1-04 + DOS-A2A-01 + DOS-INS-03"
last_result: "PASS"
---

# Demand OS — STATE

Agent czyta ten plik na starcie `/demand-os-execute`. **Nie pytaj Dowódcy** — wykonaj `next_action`.

| Pole | Wartość |
|------|---------|
| plan_status | **ACCEPTED** |
| phase | `F0_PREP_COMPLETE` — agent prep wyczerpany |
| last_step | W1-04 · A2A-01 · INS-03 → **PASS** |
| wave | 1 (roster frozen = 5) |
| organic_from | `2026-08-02` |
| ads_freeze_until | `2026-08-06` |
| build_unlocked | **false** |
| deploy | **STOP** — docs only · brak GO VPS · standing_go_closeout=false |
| next_money_check | `2026-08-03` |

## Agent-side Wave1 prep — DONE

`DOS-C*` · F0 · W1-01 · W1-02 · W1-04 · W1-05 · A2A-01 · MCP-01 · INS-01 · INS-03

## next_action (zamrożone)

```text
HARD GATE — human publish:

IF today < 2026-08-02:
  → READY_FOR_HUMAN: kręć tt_w31_install_01 (shoot plan)
  → agent: ledger hygiene only · NO code · NO dashboard · NO deploy
ELIF today >= 2026-08-02 AND DOS-W1-03 != done:
  → NEXT = DOS-W1-03 publish HITL (≥3 TT/tydz) + daily LEDGER
  → agent supports UTM/Validator/ledger rows; human publishes
ELIF DOS-LEDGER-2W / DOS-W1-PASS pending:
  → keep ledger 14d · Money Check every Pon · then W1-PASS
ELIF DOS-W1-PASS == done:
  → park ready_for_human: GO BUILD demand-f1 (no autonomous build/deploy)
```

## ready_for_human

| Item | Task / kiedy |
|------|----------------|
| Shoot + publish TT | `DOS-W1-03` ≥**2026-08-02** |
| Money Check live | Pon **2026-08-03** |
| Ledger 14d | `DOS-LEDGER-2W` |
| GO BUILD demand-f1 | po `DOS-W1-PASS` |
| VPS deploy | tylko explicit **GO DEPLOY** |

## STOP forever

HQ · dashboard P0 · S7 · QuietForge P0 · 15 agentów · multi-CTA · Mollie bez GO · deploy bez GO
