# BLAST — COI-MBA-05 (W12 Ops AI interim micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-05` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 12 spine = interim read % ops AI. Lekcja = rytuał odczytu kontraktu v1.1 już PASS (60.6%), nie nowy pomiar na VPS w tej sesji.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-05` (handoff W11) |
| Value | Mikro-lekcja: formuła + window 14d + kiedy re-window |
| SoT spine | `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` tydz. 12 |
| Scorecard | `#9 ≥60% ops AI LIVE/PASS 60.6%` — nie regresować |
| Baseline tip | `2386b47` (+ lokalne W10–W11 uncommitted) |

**Data flow:** Agent mapuje OPS-AI-01 evidence → `weeks/W12-….md` → spine Agent `[x]` tydz. 12 → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W12` Ops AI interim read.
- **Nie** generować W13–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / merge OS / `_mint_*`.
- **Nie** runtime / schema / deploy / świeży SQL na VPS (`standing_go_closeout=false`).
- **Nie** fałszować nowego PASS — lekcja cytuje istniejący wynik `60.6%`.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-05` → completed po CLOSE
- [ ] `docs/learning/weeks/W12-ops-ai-interim.md`
- [ ] Spine: status COI-MBA-05; tydz. 12 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W12-ops-ai-interim.md`
- [ ] Spine tydz. 12 Agent `[x]`, Dowódca nietknięty
- [ ] Zero runtime / deploy / VPS count
- [ ] Linki do OPS-AI-SCORECARD / OPS-AI-01 CLOSE / scorecard #9

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W13+; brak Dowódca `[x]`; brak „nowego” % bez SQL
- **Smoke:** otwórz W12 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Deploy `_ops_ai_count` bez GO
- Gate D / payment / secrets

## Estimate

≤1 sesja docs + `/handoff`.
