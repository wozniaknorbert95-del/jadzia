---
status: "[ACTIVE]"
title: "Jadzia-Core Brain (Canonical)"
owner: "Norbert Wozniak"
updated: "2026-06-02"
---

## 1) Rola modulu
`jadzia-core` to **The Brain / Nervous System** ekosystemu FlexGrafik.
Odpowiada za orkiestracje operacji (zamowienia, taski, automaty, raporty) i trzymanie stanu operacyjnego.

## 2) Source of Truth
- **Strategia makro**: `flexgrafik-meta/docs/core/master-plan.md`
- **Globalne zasady**: `flex-vcms/docs/core/global-rules.md`
- **Workflow (egzekwowany)**: `.agents/workflows/README.md` — workflow v2.0 Elite Edition (L0-L4)
- **Backlog modulu**: `todo.json` (w tym repo)
- **Plan naprawczy**: `docs/plans/PLAN-REMEDIACJI.md`

## 3) Kontrakty i dane (high level)
- Centralna baza operacyjna: `jadzia.db` — **jedyny** store stanu sesji/tasków (SQLite-only, bez JSON session files)
- Integracje: Wizard (`zzpackage.flexgrafik.nl`) oraz Gra (`app.flexgrafik.nl`)

## 4) Workflow Framework (v2.0 Elite Edition)
Sesje agentowe podążają za Golden Path: **L0: Triage → L1: Design → L2: Execute → L3: Validate → L4: Release**

| Layer | Komenda | Cel |
|-------|---------|-----|
| L0 | `/vibe-init` | Triage, klasyfikacja, kontekst |
| L0 | `/context-reset` | Reset pamięci sesji |
| L1 | `/blast` | Feature — kontrakt techniczny |
| L1 | `/blueprint` | Refactor — mapowanie zmian |
| L1 | `/migrate` | Zmiana schematu DB |
| L1 | `/dep-audit` | Review zależności |
| L2 | `/implement` | Implementacja kodu |
| L2 | `/debug` | Root Cause Analysis |
| L2 | `/profile` | Performance tuning |
| L3 | `/jadzia-test` | Pytest + smoke tests |
| L3 | `/audit-red-team` | Audyt bezpieczeństwa |
| L4 | `/jadzia-deploy` | Deploy na VPS (manual — Zasada 11) |
| L4 | `/handoff` | Zamknięcie sesji, synchronizacja stanu |
| L-CRIT | `/panic` | Awaria — przywracanie systemu |

## 5) Guardrails (twarde)
- Deploy na produkcje: **manual** (Zasada 11)
- Least privilege: skrypty/automaty nie dotykaja WP bez Dowodcy
- Brak "wszystko naraz": zasada 1-1-1
- Adversarial Thinking: każdy `/blast` wymaga `/self-review`

## 6) "Jak pracujemy" (dla agentow)
Na start sesji: wczytaj `todo.json`, ten `brain.md`, `.agents/workflows/README.md`.
