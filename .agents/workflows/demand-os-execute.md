---
description: Demand OS step runner — SET NOW → F0 Wave1 → build gates. No-ask, one next task.
---

# /demand-os-execute

## Goal

Profesjonalne wdrażanie Demand Machine **krok po kroku** bez pytań do Dowódcy.
SoT: `docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md` v5.
Plan: `docs/ops/DEMAND-OS-ACTION-PLAN.md`.
TODO: `docs/ops/DEMAND-OS-TODO.md`.
State: `docs/ops/demand-os/STATE.md`.

## Hard rules

1. **No-ask** — wybierz `next_action` ze STATE; wykonaj; zaktualizuj status.
2. **1-1-1** — jedna sesja = jeden pending DOS-* (lub Phase0 verify).
3. **Zero kodu produktu** aż `DOS-W1-PASS` + explicit `GO BUILD demand-f1`.
4. **STOP:** HQ · S7 · QuietForge P0 · Ads w freeze · 15 agentów · multi-CTA.
5. Human-only → status `ready_for_human` + checklist; **nie blokuj** sesji pytaniem.

## Procedure

### 1. Hydrate

Read in order:

1. `docs/ops/demand-os/STATE.md`
2. `docs/ops/DEMAND-OS-TODO.md` (first `pending` with deps satisfied)
3. `docs/ops/marketing/OPERATOR-TODAY.md`
4. `docs/ops/demand-os/set-now/README.md`

### 2. Verify Phase 0

```bash
python tools/demand_os_phase0_check.py
```

- FAIL → napraw brakujące artefakty w `docs/ops/demand-os/set-now/`, nie idź dalej.
- PASS → kontynuuj wg STATE `next_action`.

### 3. Execute one task

| Gdy | Zrób |
|-----|------|
| Phase 0 incomplete | Uzupełnij set-now pack; re-run check |
| `today < 2026-08-02` | Prep: brief/shoot-plan/Validator drill; **nie** publish TT |
| `today >= 2026-08-02` i Wave1 open | Wspieraj HITL: UTM linki, ledger row, Validator PASS log, STL template — park fizyczny publish jako `ready_for_human` jeśli brak dostępu do konta |
| `DOS-W1-PASS` pending | Audyt ledger (≥3 TT/tydz × 2 tyg.); ustaw PASS tylko na dowodach |
| Build | Tylko po `DOS-F1-GO` zapisane przez Dowódcę |

### 4. Close step

1. Ustaw status taska w `DEMAND-OS-TODO.md` (`done` / `ready_for_human` / `blocked`).
2. Zaktualizuj `STATE.md` (`phase`, `next_action`).
3. Krótki handoff w `docs/handoffs/` jeśli sesja się kończy.
4. **Nie pytaj** „co dalej?” — wpisz następny `next_action`.

## Output format

```text
DEMAND_OS_STEP: [DOS-id | PHASE0_CHECK]
RESULT: [PASS | FAIL | READY_FOR_HUMAN]
EVIDENCE: [paths]
NEXT_ACTION: [from STATE]
BUILD_UNLOCKED: [false|true]
```

## Done when

Jeden krok domknięty + STATE zsynchronizowany + Phase0 check zielony (jeśli w Phase 0/F0).
