# Knowledge System Index — FlexGrafik

**Status:** PARTIAL (COI-KNOW-00) — index w jadzia only; **meta + VCMS jeszcze bez mirror linku**  
**Date:** 2026-07-18 (truth repair)  
**Cel:** Jedna hierarchy SoT — zero sprzecznych kanonów.

## Hierarchy (od najwyższego)

| Pri | Warstwa | Ścieżka / host | Co tam żyje |
|-----|---------|----------------|-------------|
| 1 | Konstytucja ekosystemu | `flexgrafik-meta/docs/core/` | global-rules, workflow-manual, master-plan, module specs, COI charter |
| 2 | Brain modułu | `jadzia-core/brain.md`, `AGENTS.md`, `todo.json` | stan operacyjny Jadzia / active_gate |
| 3 | Governance runtime | `https://cmd.flexgrafik.nl` (+ `/docs/`) | VCMS scan, conflicts, mapa repo, rytuał sesji |
| 4 | Design / kontrakty COI | `jadzia-core/docs/design/coi-commander/` | ADR, specs D0.x, UX brief |
| 5 | Ops runbooks | `jadzia-core/docs/ops/` | deploy, dogfood, scorecard, **PROCESS-CATALOG**, OPS-AI |
| 6 | Learning (AI MBA) | `jadzia-core/docs/learning/` | spine 52 tyg., weeks/WXX |
| 7 | Handoffy (ephemeral) | `jadzia-core/docs/handoffs/` | dowód sesji; **nie** nadpisują konstytucji |

## Reguła anty-duplikacji

| Treść | Gdzie kanon | Nie kopiuj do |
|-------|-------------|----------------|
| Zasady globalne 1-1-1, deploy, języki | flexgrafik-meta (+ VCMS mirror jeśli obowiązuje) | długie paste w handoff |
| Active gate / backlog Jadzia | `todo.json` | drugi backlog w meta |
| Konflikty repo / scan | VCMS `conflicts.md` | lokalne „conflict notes” bez skanu |
| URL prod hub / OS / VCMS | ADR D0.6 | hardcoded sprzeczne localhost w UI |
| Proces biznesowy L1 | `docs/ops/PROCESS-CATALOG.md` (po PROC-00) | rozproszone „jak robimy X” w 5 handoffach |
| Lekcja MBA Week N | `docs/learning/weeks/` | Notion-only bez linku do wdrożenia |

## Linki kluczowe

- Scorecard zaliczenia: [SCORECARD-AI-OS-ZALICZENIE.md](./SCORECARD-AI-OS-ZALICZENIE.md)
- Process catalog: [PROCESS-CATALOG.md](./PROCESS-CATALOG.md) (baseline → PROC-01)
- OPS AI: [OPS-AI-SCORECARD.md](./OPS-AI-SCORECARD.md)
- AI MBA spine: [../learning/AI-MBA-FLEXGRAFIK-SPINE.md](../learning/AI-MBA-FLEXGRAFIK-SPINE.md)
- Phone hub ADR: [../design/coi-commander/adr/D0.6-phone-hub-not-merge.md](../design/coi-commander/adr/D0.6-phone-hub-not-merge.md)

## Konflikt resolution

1. Meta konstytucja wygrywa nad lokalnym brain przy sprzeczności zasad.  
2. `todo.json` wygrywa nad handoffem przy active_gate.  
3. ADR D0.x wygrywa nad komentarzem w UI.  
4. Handoff aktualizuje scorecard status, nie odwrotnie bez dowodu.
