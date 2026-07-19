# BLAST — COI-MBA-06 (W13 Q1 gate review micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-06` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 13 = Q1 gate review. Lekcja = scorecard #1–9 LIVE + week log Agent (W0–W12) — nie fałszywy „program zaliczony” bez Dowódcy.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-06` (handoff W12) |
| Value | Q1 CLOSE: cele kwartału vs evidence; otwarte human PASS |
| SoT spine | `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` tydz. 13 |
| Scorecard | `#1–9 LIVE` — nie regresować |
| Baseline tip | `2386b47` (+ lokalne W10–W12 uncommitted) |

**Data flow:** Agent czyta spine Q1 + scorecard → `weeks/W13-….md` (week log) → spine Agent `[x]` tydz. 13 → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W13` Q1 gate review.
- **Nie** generować W14–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / merge OS / `_mint_*`.
- **Nie** runtime / deploy (`standing_go_closeout=false`).
- **Nie** oznaczać „MBA Year PASS” — tylko Q1 Agent review.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-06` → completed po CLOSE
- [ ] `docs/learning/weeks/W13-q1-gate-review.md`
- [ ] Spine: status COI-MBA-06; tydz. 13 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W13-q1-gate-review.md`
- [ ] Spine tydz. 13 Agent `[x]`, Dowódca nietknięty
- [ ] Week log pokrywa Q1 Agent evidence; scorecard link
- [ ] Zero runtime / deploy

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W14+; brak Dowódca `[x]`; brak Year PASS
- **Smoke:** otwórz W13 — linki resolvują w repo

## STOP

- Fałszywy Dowódca / Year PASS
- Catch-up wszystkich 52 weeks
- Gate D / payment / secrets

## Estimate

≤1 sesja docs + `/handoff`.
