---
status: "[DRAFT]"
title: "Jadzia-Core Brain (Canonical)"
owner: "Norbert Wozniak"
updated: "2026-04-09"
---

## 1) Rola modulu
`jadzia-core` to **The Brain / Nervous System** ekosystemu FlexGrafik.
Odpowiada za orkiestracje operacji (zamowienia, taski, automaty, raporty) i trzymanie stanu operacyjnego.

## 2) Source of Truth
- **Strategia makro**: `flexgrafik-meta/docs/core/master-plan.md`
- **Globalne zasady**: `flex-vcms/docs/core/global-rules.md`
- **Workflow (egzekwowany)**: `flexgrafik-meta/docs/core/workflow-manual.md`
- **Backlog modulu**: `todo.json` (w tym repo)

## 3) Kontrakty i dane (high level)
- Centralna baza operacyjna: `jadzia.db` (lokalizacja i schema zdefiniowane w dokumentacji/ops)
- Integracje: Wizard (`zzpackage.flexgrafik.nl`) oraz Gra (`app.flexgrafik.nl`)

## 4) Guardrails (twarde)
- Deploy na produkcje: **manual** (Zasada 11)
- Least privilege: skrypty/automaty nie dotykaja WP bez Dowodcy
- Brak \"wszystko naraz\": zasada 1-1-1

## 5) \"Jak pracujemy\" (dla agentow)
Na start sesji: wczytaj `todo.json`, ten `brain.md`, oraz odpowiednie dokumenty z `flexgrafik-meta` i `flex-vcms`.

