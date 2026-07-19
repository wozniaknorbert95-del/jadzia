# BLAST — COI-MBA-13 (W20 Board assistant depth micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-13` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 20 = głębokość AI Asystent Zarządu (jakość briefu + higiena ticketów). Lekcja = STRATEGY-HITL LIVE + W11 ritual — nie nowy spawn / nie auto-execute.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-13` (handoff W19) |
| Value | Mikro-lekcja: quality bar brief + hygiene `brief_hitl` |
| SoT | D0.20 §5 + P-BOARD-01 + STRATEGY-HITL-01 |
| Spine | tydz. 20 (Agent `[ ]` → `[x]` po lekcji) |
| Baseline tip | `2386b47` (+ lokalne W10–W19 uncommitted) |

**Data flow:** Agent mapuje board LIVE → `weeks/W20-….md` → spine Agent `[x]` → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W20` Board assistant depth.
- **Nie** generować W21–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / `_mint_*` / auto-execute brief.
- **Nie** runtime / deploy / fresh brief spawn w tej sesji.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-13` → completed po CLOSE
- [ ] `docs/learning/weeks/W20-board-assistant-depth.md`
- [ ] Spine: status COI-MBA-13; tydz. 20 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W20-board-assistant-depth.md`
- [ ] Spine tydz. 20 Agent `[x]`, Dowódca nietknięty
- [ ] Linki D0.20 + W11 + STRATEGY CLOSE + P-BOARD-01
- [ ] Zero runtime / auto-execute

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W21+; brak Dowódca `[x]`
- **Smoke:** otwórz W20 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Auto SSH/publish/pay z briefu
- Gate D / secrets

## Estimate

≤1 sesja docs + `/handoff`.
