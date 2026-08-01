---
status: "[SESSION CLOSE · READY FOR NEXT]"
title: "Demand OS v5 — handoff + START PROMPT następnej sesji"
updated: "2026-07-31"
gate: "DEMAND-OS-PLAN-00"
branch: "master"
prod_tip: "fcf6a9f / cache vhq-w68a"
---

# HANDOFF — 2026-07-31 Demand OS TARGET v5

## DONE (sesja)

| Deliverable | Status |
|-------------|--------|
| [`docs/ops/SYSTEM-FIRM-OPERATING-MAP.md`](../SYSTEM-FIRM-OPERATING-MAP.md) | AS-IS działy (Mermaid) |
| [`docs/ops/strategy/STRATEGY-PACK.md`](../strategy/STRATEGY-PACK.md) | ACCEPTED · SOT snajper |
| [`docs/ops/strategy/README.md`](../strategy/README.md) | index doktryny |
| [`docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`](../SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md) | **v5 INSIDER · ACCEPTED · SOT egzekucji** |
| [`docs/ops/marketing/OPERATOR-TODAY.md`](../marketing/OPERATOR-TODAY.md) | pointer SET NOW |
| [`docs/ops/PROGRAM-LANES-SOT.md`](../PROGRAM-LANES-SOT.md) | pasy S + O |
| [`AGENTS.md`](../../AGENTS.md) | pointer strategii/OS |

**Werdykt strategiczny (zamrożony):**
- Problem = **NIE MA KLIENTÓW** (nie ops po sprzedaży)
- Ops post-sale = **OUT OF SCOPE** (już OK)
- OS = Demand Machine + hub-spoke agentic + insider layer
- Snajper: 1 ICP/week · 1 CTA Wizard · polowanie (TT/FB comments) > vanity
- Wave 1: Growth Lead + ICP + TT + Sales + Sniper Validator

**Git:** branch `master` · HEAD `2402e93` · **docs niecommitowane** (świadomie).

---

## LEFT (następna sesja — TO JEST CEL)

**Profesjonalny plan działania klasy enterprise** (vibe coding + agentic engineering):
- 100% spójność z [`SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`](../SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md)
- TODO per zadanie z **Definition of Done**
- Mapowanie 1:1: SET NOW (C) · Waves W1–W4 · Fazy F0–F5 · agenci · MCP/A2A
- **Zero kodu** w sesji planu — tylko plan + todo.json / plan doc po ACCEPT

---

## RISKS

| Ryzyko | Mitigacja |
|--------|-----------|
| Powrót do HQ/ops desk | OS §N manowce + scope_kill |
| Plan bez UTM/ledger | sekcja C obowiązkowa w planie |
| 15 agentów Day 1 | Wave 1 tylko 5 ról |
| Stare handoffy (MKT-DASH) | **superseded** przez OS TARGET v5 |
| Commit bez review | Dowódca decyduje — dziś uncommitted OK |

---

## CRITICAL WARNINGS

- **SoT egzekucji:** tylko `SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md` v5 — nie REVENUE-PROCESS-GAP-MAP jako kierunek
- **Ads FREEZE** do 2026-08-06 · organic ≥2026-08-02
- **Deploy / Mollie / S7** — tylko explicit GO
- **Nie stage:** `docs/ops/marketing/MKT/` dirty pack

---

## START PROMPT — wklej w nową sesję

```text
@vibe-init

KONTEKST: FlexGrafik / jadzia-core. 2 lata budowy systemu. Cel sesji: PROFESJONALNY PLAN DZIAŁANIA ENTERPRISE (vibe coding + agentic engineering) w 100% zgodny z SoT egzekucji.

KANON (przeczytaj w całości przed planem):
1. C:/Users/FlexGrafik/FlexGrafik/github/jadzia-core/docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md  ← JEDYNY SoT EGZEKCJI (v5 INSIDER)
2. C:/Users/FlexGrafik/FlexGrafik/github/jadzia-core/docs/ops/strategy/STRATEGY-PACK.md
3. C:/Users/FlexGrafik/FlexGrafik/github/jadzia-core/docs/ops/SYSTEM-FIRM-OPERATING-MAP.md (AS-IS)
4. docs/handoffs/2026-07-31-DEMAND-OS-PLAN-00-HANDOFF.md

PROBLEM NR 1 (nie negocjuj): NIE MA KLIENTÓW. Ops po sprzedaży = OUT OF SCOPE (już świetne).

ZADANIE SESJI:
Napisz ENTERPRISE ACTION PLAN + TODO z DoD dla każdego zadania. Plan musi mapować 1:1:
- Sekcja C (CO USTAWIĆ TERAZ) — ledger, UTM, ICP week1, FB allowlist, Validator
- Wave 1→4 (agent rollout)
- F0→F5 (build fazy demand-f1…f5)
- Hub-spoke: Growth Lead, ICP Brain, TT, FB hunter, Blog ICP, Sales STL, Sniper Validator
- MCP/A2A handoffs z OS TARGET
- Insider: signal stack, comment>post, STL<15m, creative fatigue, kill dual cash (Design Agent→Wizard)

DELIVERABLES (docs only — zero kodu produktu):
- docs/ops/DEMAND-OS-ACTION-PLAN.md (plan główny + mermaid)
- docs/ops/DEMAND-OS-TODO.md LUB wpis w todo.json gate DEMAND-OS-PLAN-00 (każdy task: id, owner, deps, DoD, os_target_section_ref)
- Aktualizacja OPERATOR-TODAY pointer

REGUŁY PLANU:
- MAX EFFECT · MIN COMPLEXITY · snajper 1 CTA Wizard
- Każde zadanie musi cite sekcję OS TARGET (np. "C.1 #3", "Wave1", "F1", "Agent_FB")
- DoD musi być weryfikowalne (np. "100% growth links mają UTM", nie "lepszy marketing")
- STOP: HQ polish, S7, ops desk, 15 agentów Day1, multi-CTA, QuietForge P0, Mollie bez GO

KOLEJNOść W PLANIE:
1. SET NOW (human/HITL) — F0 Wave1
2. Ledger 2 tygodnie
3. GO BUILD demand-f1… po PASS F0
4. Wave 2 dopiero po Wave1 PASS

Po planie: handoff z ACCEPT DEMAND-OS-ACTION-PLAN.

Język: PL (Dowódca). UI/copy przykłady: NL.
```

---

## NEXT SESSION COMMAND

`@vibe-init` + START PROMPT powyżej

---

## V-FILES

1. `C:/Users/FlexGrafik/FlexGrafik/github/jadzia-core/docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md`
2. `C:/Users/FlexGrafik/FlexGrafik/github/jadzia-core/docs/ops/strategy/STRATEGY-PACK.md`
3. `C:/Users/FlexGrafik/FlexGrafik/github/jadzia-core/docs/ops/marketing/OPERATOR-TODAY.md`
4. `C:/Users/FlexGrafik/FlexGrafik/github/jadzia-core/docs/handoffs/2026-07-31-DEMAND-OS-PLAN-00-HANDOFF.md`
