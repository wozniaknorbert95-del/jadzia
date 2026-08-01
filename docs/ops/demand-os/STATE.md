---
status: "[ACTIVE · CONTINUOUS PREP]"
title: "Demand OS — execution state machine"
updated: "2026-08-01"
gate: "DEMAND-OS-SET-NOW-00"
last_step: "captions+reply+fatigue+ledger-ops+GO-DAY"
last_result: "PASS"
---

# Demand OS — STATE

**Nie zatrzymuj się na „wait”.** Agent produkuje prep aż organic; potem wspiera publish/ledger.

| Pole | Wartość |
|------|---------|
| phase | `F0_PREP_PLUS` — continuous content ops |
| organic_from | `2026-08-02` |
| ads_freeze_until | `2026-08-06` |
| build_unlocked | **false** |
| git_remote | **PUSHED** `origin/master` @ `c7b41b6` |
| deploy_vps | **STOP** bez GO DEPLOY |
| ledger_2w | `in_progress` |
| next_money_check | `2026-08-03` |

## next_action

```text
IF today < 2026-08-02:
  → keep enriching set-now pack (captions/replies/calendar) · ledger hygiene
  → commit docs often · NO deploy · NO product code
ELIF today >= 2026-08-02:
  → execute GO-DAY checklist support · DOS-W1-03
  → daily: python tools/demand_os_ledger_day.py + Validator rows
ELIF DOS-W1-PASS:
  → park GO BUILD demand-f1 (human)
```

## ready_for_human (nie blokuje agenta)

`GO-DAY-2026-08-02.md` · publish TT · potem ledger 14d
