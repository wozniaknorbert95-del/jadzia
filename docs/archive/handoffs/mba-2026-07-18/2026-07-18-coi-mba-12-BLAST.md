# BLAST — COI-MBA-12 (W19 CS implement micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-12` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 19 = lekcja o **wdrożonym** CS API+UI HITL (`COI-CS-02`). Lekcja = CLOSE już LIVE — nie nowy kod / nie auto-trigger.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-12` (handoff W18) |
| Value | Mikro-lekcja: spawn → queue → disposition; dogfood tip |
| SoT | `docs/handoffs/2026-07-18-coi-cs-02-CLOSE.md` |
| Spine | tydz. 19 (Agent `[x]` z truth-repair — week file teraz) |
| Baseline tip | `2386b47` (+ lokalne W10–W18 uncommitted) |

**Data flow:** Agent mapuje CS-02 CLOSE → `weeks/W19-….md` → spine status → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W19` CS implement.
- **Nie** generować W20–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / `_mint_*` / auto-email / auto paid-order trigger.
- **Nie** runtime / deploy / nowy CS code.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-12` → completed po CLOSE
- [ ] `docs/learning/weeks/W19-cs-implement.md`
- [ ] Spine: status COI-MBA-12; tydz. 19 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W19-cs-implement.md`
- [ ] Spine tydz. 19 Agent `[x]`, Dowódca nietknięty
- [ ] Linki CS-02 CLOSE + W18 + P-CS-01 + scorecard #6
- [ ] Zero runtime / deploy

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W20+; brak Dowódca `[x]`
- **Smoke:** otwórz W19 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Auto-trigger paid orders
- Gate D / secrets / helpdesk merge

## Estimate

≤1 sesja docs + `/handoff`.
