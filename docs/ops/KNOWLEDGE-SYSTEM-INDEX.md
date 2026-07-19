# Knowledge System Index — FlexGrafik

**Status:** LIVE (ECO-POLISH-01) — SoT w jadzia + mirror pointery w meta i VCMS  
**Date:** 2026-07-19  
**Cel:** Jedna hierarchy SoT — zero sprzecznych kanonów.

## Hierarchy (od najwyższego)

| Pri | Warstwa | Ścieżka / host | Co tam żyje |
|-----|---------|----------------|-------------|
| 1 | Konstytucja ekosystemu | `flexgrafik-meta/docs/core/` | **pełne** global-rules, workflow-manual, master-plan, module specs, COI charter |
| 2 | Brain modułu | per-repo `brain.md` / `todo.json` | stan operacyjny / active_gate |
| 3 | Governance runtime | `https://cmd.flexgrafik.nl` (+ `/docs/`) | VCMS scan, conflicts, mapa, **ops handbooks** |
| 4 | Design / kontrakty COI | `jadzia-core/docs/design/coi-commander/` | ADR, specs D0.x, UX brief |
| 5 | Ops runbooks | `jadzia-core/docs/ops/` | deploy, dogfood, scorecard, **PROCESS-CATALOG**, OPS-AI, **marketing OS** (`docs/ops/marketing/`) |
| 6 | Learning (AI MBA) | `jadzia-core/docs/learning/` | spine 52 tyg., weeks/WXX |
| 7 | Handoffy (ephemeral) | `*/docs/handoffs/` | dowód sesji; **nie** nadpisują konstytucji |

## cmd surfaces (governance UI docs)

| Surface | URL / path | Rola |
|---------|------------|------|
| Command Center | https://cmd.flexgrafik.nl | Dashboard + Baza Wiedzy |
| Surfaces map | `/docs/study/surfaces-map` | Kiedy Commander / VCMS / OS / Wizard |
| **COI Commander handbook** | `/docs/study/coi-commander-ops-handbook` | Playbook CEO (treść na cmd) |
| Commander **UI** | https://api.zzpackage.flexgrafik.nl/commander/ | Hub dnia — **nie** hostowany na cmd |
| AI OS Knowledge mirror | `/docs/ecosystem/ai-os-knowledge` | Pointer → ten plik |
| AI OS Processes mirror | `/docs/ecosystem/ai-os-processes` | Pointer → PROCESS-CATALOG |

## Learning — dwa tracki (nie mieszać)

| Track | SoT | Na cmd |
|-------|-----|--------|
| Skill map T1–T7 | `vibe-coach/docs/study-index.md` | pointer w VCMS `docs/study/study-index.md` |
| AI MBA W00–W52 | `jadzia-core/docs/learning/` | pointer via AI OS Knowledge |

## Mirrors — pointer only

| Host | Pointer | Rola |
|------|---------|------|
| flexgrafik-meta | `docs/core/knowledge-system-index.md` | konstytucja → ten SoT |
| flexgrafik-meta | `docs/core/global-rules.md` | **jedyna pełna treść zasad** |
| Flex-vcms | `docs/core/global-rules.md` | **pointer** → meta (COI-KNOW-02) |
| Flex-vcms | `docs/ecosystem/ai-os-knowledge.md` | → ten SoT |
| Flex-vcms | `docs/ecosystem/ai-os-processes.md` | → PROCESS-CATALOG |
| flexgrafik-meta | `docs/core/process-catalog-index.md` | → PROCESS-CATALOG |
| GitHub SoT | [KNOWLEDGE-SYSTEM-INDEX.md](https://github.com/wozniaknorbert95-del/jadzia/blob/master/docs/ops/KNOWLEDGE-SYSTEM-INDEX.md) | kanoniczny blob |

## Reguła anty-duplikacji

| Treść | Gdzie kanon | Nie kopiuj do |
|-------|-------------|----------------|
| Zasady globalne 1-1-1, deploy, języki | **flexgrafik-meta** `global-rules` | pełna kopia w VCMS / handoff |
| Active gate / backlog | per-repo `todo.json` | drugi backlog w meta |
| Konflikty repo / scan | VCMS `conflicts.md` | lokalne notatki bez skanu |
| URL prod hub / OS / VCMS | ADR D0.6 + surfaces-map | sprzeczne localhost w UI |
| Commander operator playbook | VCMS `docs/study/coi-commander-ops-handbook` | paste ADR D0.x do VCMS |
| ADR / UX specs Commander | jadzia `docs/design/coi-commander/` | pełne ADR na cmd |
| Proces biznesowy L1 | `PROCESS-CATALOG.md` | rozproszone „jak robimy X” |
| Lekcja MBA Week N | `docs/learning/weeks/` | Notion-only / VitePress paste |
| Skill map T1–T7 | vibe-coach | hostowanie lekcji na cmd |
| Statusy AI OS zaliczenia | `SCORECARD-AI-OS-ZALICZENIE.md` | paste tabeli do meta/VCMS |

## Linki kluczowe

- Scorecard: [SCORECARD-AI-OS-ZALICZENIE.md](./SCORECARD-AI-OS-ZALICZENIE.md)
- Process catalog: [PROCESS-CATALOG.md](./PROCESS-CATALOG.md)
- OPS AI: [OPS-AI-SCORECARD.md](./OPS-AI-SCORECARD.md)
- AI MBA spine: [../learning/AI-MBA-FLEXGRAFIK-SPINE.md](../learning/AI-MBA-FLEXGRAFIK-SPINE.md)
- Phone hub ADR: [../design/coi-commander/adr/D0.6-phone-hub-not-merge.md](../design/coi-commander/adr/D0.6-phone-hub-not-merge.md)
- Operator playbook (cmd): `Flex-vcms/flex-vcms/docs/study/coi-commander-ops-handbook.md`
- Design folder pointer: [../design/coi-commander/OPERATOR-PLAYBOOK.md](../design/coi-commander/OPERATOR-PLAYBOOK.md)
- **Marketing OS (FG):** [marketing/README.md](./marketing/README.md) — unit economics, L0–L5; QuietForge marketing → `services/docs/strategy/` only

## Docs IA + Archive policy (ECO-POLISH-01)

| Reguła | Znaczenie |
|--------|-----------|
| **I-1** | 1 brain + 1 todo kanoniczne per repo (zzp: thin `brain.md` → `MASTER-BRAIN.md` SoT + `docs/audit-todo.json`) |
| **I-2** | Pełne `global-rules` / `workflow-manual` **tylko** w `flexgrafik-meta/docs/core/` |
| **I-3** | KNOW / PROCESS / scorecard **tylko** w `jadzia-core/docs/ops/` |
| **I-4** | cmd VitePress **nie** hostuje ADR D0.x, MBA weeks, product-master, skill map T1–T7 |
| **I-5** | Antigravity / Gemini CLI **nigdy** w LIVE nav / README / AGENTS jako aktywny stack |
| **I-6** | Handoffs **rolling** w `docs/handoffs/` (≤15 plików lub ≤30 dni); cold → `docs/archive/handoffs/` |
| Archive ≫ delete | Evidence idzie do archive; delete tylko sekrety, tokeny, tarballe, binary junk |
| VitePress | `srcExclude: ['**/archive/**']` — cold poza buildem; nie czytaj archive default |
| Entry | Agent / Dowódca w ≤60s wie: SoT, LIVE vs historia |

## Konflikt resolution

1. Meta konstytucja wygrywa nad lokalnym brain przy sprzeczności zasad.  
2. `todo.json` wygrywa nad handoffem przy active_gate.  
3. ADR D0.x wygrywa nad komentarzem w UI.  
4. Handoff aktualizuje scorecard status, nie odwrotnie bez dowodu.  
5. VCMS `global-rules` pointer nie może wrócić do pełnej kopii bez decyzji Dowódcy.
6. Archive off-nav; rolling handoffs ≤15 — nie wracaj PH4/journal/lab do LIVE sidebar.
