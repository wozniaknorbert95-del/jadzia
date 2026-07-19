# BLAST — COI-MBA-04 (W11 Board brief HITL micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-04` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 11 spine = rytuał weekly board brief HITL. Lekcja = `COI-STRATEGY-HITL-01` już LIVE, nie nowe API.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-04` (handoff W10) |
| Value | Mikro-lekcja: brief metrics → spawn HITL tickets → Home approve/act |
| SoT spine | `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` tydz. 11 |
| Scorecard | `#7 AI Asystent Zarządu LIVE` — nie regresować |
| Baseline tip | `2386b47` (+ lokalne W10 uncommitted) |

**Data flow:** Agent mapuje dowody STRATEGY LIVE → `weeks/W11-….md` → spine Agent `[x]` tydz. 11 → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W11` Board brief ritual.
- **Nie** generować W12–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / merge OS / `_mint_*`.
- **Nie** runtime Python / schema / deploy (`standing_go_closeout=false`).

## A — Actions

- [ ] `todo.json`: add `COI-MBA-04` → completed po CLOSE
- [ ] `docs/learning/weeks/W11-board-brief-hitl.md`
- [ ] Spine: status COI-MBA-04; tydz. 11 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W11-board-brief-hitl.md`
- [ ] Spine tydz. 11 Agent `[x]`, Dowódca nietknięty
- [ ] Zero runtime / deploy
- [ ] Linki do STRATEGY-HITL / P-BOARD-01 / scorecard #7

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W12+; brak Dowódca `[x]`
- **Smoke:** otwórz W11 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Auto-execute brief tickets (lekcja podkreśla HITL-only)
- Gate D / payment / secrets

## Estimate

≤1 sesja docs + `/handoff`.
