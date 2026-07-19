# BLAST — COI-MBA-10 (W17 PM Agent OS ritual micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-10` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 17 = rytuał PM HITL w Agent OS. Lekcja = `COI-PM-01` już PASS — nie merge OS↔jadzia, nie nowy approve w tej sesji.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-10` (handoff W16) |
| Value | Mikro-lekcja: hop OS → jedna approve HITL → DONE |
| SoT | COI-PM-01 CLOSE + D0.20 §3 + D0.6 (no merge) |
| Spine | tydz. 17 (Agent `[x]` już z truth-repair — week file teraz) |
| Baseline tip | `2386b47` (+ lokalne W10–W16 uncommitted) |

**Data flow:** Agent mapuje PM-01 evidence → `weeks/W17-….md` → spine status update → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W17` PM Agent OS ritual.
- **Nie** generować W18–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** merge Agent OS → jadzia (ADR D0.6).
- **Nie** Gate D / Mollie / sekrety / `_mint_*`.
- **Nie** runtime / deploy / fresh approve w tej sesji.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-10` → completed po CLOSE
- [ ] `docs/learning/weeks/W17-pm-agent-os-ritual.md`
- [ ] Spine: status COI-MBA-10; tydz. 17 Agent pozostaje `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W17-pm-agent-os-ritual.md`
- [ ] Spine tydz. 17 Agent `[x]`, Dowódca nietknięty
- [ ] Linki PM-01 CLOSE + D0.20 + P-ENG-01 + D0.6
- [ ] Zero merge OS / runtime approve

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W18+; brak Dowódca `[x]`; brak merge
- **Smoke:** otwórz W17 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Merge OS↔jadzia
- Gate D / secrets

## Estimate

≤1 sesja docs + `/handoff`.
