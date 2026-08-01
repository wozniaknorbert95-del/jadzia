---
status: "[SESSION CLOSE · READY FOR ACCEPT]"
title: "DEMAND-OS-ACTION-PLAN — written · zero kodu"
updated: "2026-07-31"
gate: "DEMAND-OS-PLAN-00"
branch: "master"
prod_tip: "fcf6a9f / cache vhq-w68a"
---

# HANDOFF — 2026-07-31 DEMAND OS Action Plan

## DONE

| Deliverable | Status |
|-------------|--------|
| [`docs/ops/DEMAND-OS-ACTION-PLAN.md`](../ops/DEMAND-OS-ACTION-PLAN.md) | READY FOR ACCEPT · mapowanie C / W1–W4 / F0–F5 / hub-spoke / MCP-A2A / insider |
| [`docs/ops/DEMAND-OS-TODO.md`](../ops/DEMAND-OS-TODO.md) | wszystkie DOS-* + DoD + `os_target_section_ref` |
| [`docs/ops/marketing/OPERATOR-TODAY.md`](../ops/marketing/OPERATOR-TODAY.md) | pointer → ACTION PLAN + DOS-C* |
| [`todo.json`](../../todo.json) | `active_plan` → ACTION PLAN · next = SET NOW HITL |

**SoT egzekucji (niezmieniony):** [`SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`](../ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md) v5 INSIDER.

**Zakres sesji:** docs only · zero kodu produktu · zero deploy · MKT dirty pack nietknięty.

---

## ACCEPT

```text
ACCEPT DEMAND-OS-ACTION-PLAN
```

Po ACCEPT: egzekucja = [`DEMAND-OS-TODO.md`](../ops/DEMAND-OS-TODO.md) Phase 0 (`DOS-C1-01` … `DOS-C7-01`).

---

## LEFT (human / następna sesja)

1. **SET NOW HITL** — Phase 0 TODO (ledger, UTM, ICP installateur, FB allowlist, Validator, Wave1 roster=5)
2. ≥2026-08-02: `GO TIKTOK ORGANIC` · F0 Wave1
3. Ledger 2 tygodnie → `DOS-W1-PASS`
4. Dopiero potem: `GO BUILD demand-f1` … f5 · Wave 2+

---

## RISKS

| Ryzyko | Mitigacja |
|--------|-----------|
| Skok do kodu przed SET NOW | ACTION PLAN §O · DOS-F1-GO deps |
| HQ / ops desk creep | STOP list §N · `DOS-STOP-*` = wont_do |
| 15 agentów Day1 | C.6 · Wave1 = 5 ról |
| Ads w freeze | C.1 #5 · do 2026-08-06 |

---

## CRITICAL WARNINGS

- SoT egzekucji = OS TARGET v5 — ACTION PLAN go mapuje, nie zastępuje
- Ads FREEZE do 2026-08-06 · organic ≥2026-08-02
- Deploy / Mollie / S7 — tylko explicit GO
- Nie stage: `docs/ops/marketing/MKT/` dirty pack

---

## NEXT

**Human:** `ACCEPT DEMAND-OS-ACTION-PLAN` → otwórz OPERATOR-TODAY → `DOS-C1-01`.

**Agent (po ACCEPT):** wspierać HITL SET NOW / F0 — **bez** product code do W1 PASS + `GO BUILD demand-f1`.

---

## V-FILES

1. `docs/ops/DEMAND-OS-ACTION-PLAN.md`
2. `docs/ops/DEMAND-OS-TODO.md`
3. `docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`
4. `docs/ops/marketing/OPERATOR-TODAY.md`
)
