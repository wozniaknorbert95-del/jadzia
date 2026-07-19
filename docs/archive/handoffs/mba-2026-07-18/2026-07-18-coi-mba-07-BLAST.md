# BLAST — COI-MBA-07 (W14 HITL vs HOTL micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-07` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Start Q2 — tydz. 14 = polityka HITL vs HOTL + użycie progów D0.11. Lekcja = spec już w repo + F3 graduation LIVE; nie nowa automatyka ani live graduate.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-07` (handoff W13 / Q2 start) |
| Value | Mikro-lekcja: kiedy HITL, kiedy HOTL, progi, revert |
| SoT | `docs/design/coi-commander/specs/D0.11-graduation.md` |
| Spine | tydz. 14 |
| Baseline tip | `2386b47` (+ lokalne W10–W13 uncommitted) |

**Data flow:** Agent mapuje D0.11 + F3 evidence → `weeks/W14-….md` → spine Agent `[x]` → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W14` HITL vs HOTL.
- **Nie** generować W15–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / `_mint_*`.
- **Nie** runtime / deploy / live HOTL graduate w tej sesji.
- Always-HITL (publish CRITICAL, deploy, Gate D, payment) — **nie** graduate.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-07` → completed po CLOSE
- [ ] `docs/learning/weeks/W14-hitl-vs-hotl.md`
- [ ] Spine: status COI-MBA-07; tydz. 14 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W14-hitl-vs-hotl.md`
- [ ] Spine tydz. 14 Agent `[x]`, Dowódca nietknięty
- [ ] Linki do D0.11 + F3/v3 proof + OPS safe list
- [ ] Zero runtime / deploy / live graduate

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W15+; brak Dowódca `[x]`
- **Smoke:** otwórz W14 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Auto-graduate CRITICAL / payment / Gate D
- Gate D / secrets

## Estimate

≤1 sesja docs + `/handoff`.
