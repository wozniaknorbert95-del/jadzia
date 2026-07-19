# BLAST — COI-MBA-11 (W18 CS BLAST micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-11` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 18 = lekcja o **scope-lock** CS (`COI-CS-01` BLAST). Implementacja = W19 / CS-02 — nie mieszać w tej sesji.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-11` (handoff W17) |
| Value | Mikro-lekcja: pre-sale≠post-sale; thin slice `cs_followup`; STOP list |
| SoT | `docs/handoffs/2026-07-18-coi-cs-01-BLAST.md` |
| Spine | tydz. 18 (Agent `[x]` z truth-repair — week file teraz) |
| Baseline tip | `2386b47` (+ lokalne W10–W17 uncommitted) |

**Data flow:** Agent mapuje CS-01 BLAST → `weeks/W18-….md` → spine status → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W18` CS BLAST scope.
- **Nie** generować W19–W52 (W19 = osobny gate CS implement).
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / `_mint_*` / merge OS / helpdesk.
- **Nie** runtime / deploy / nowy CS code.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-11` → completed po CLOSE
- [ ] `docs/learning/weeks/W18-cs-blast.md`
- [ ] Spine: status COI-MBA-11; tydz. 18 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W18-cs-blast.md`
- [ ] Spine tydz. 18 Agent `[x]`, Dowódca nietknięty
- [ ] Linki CS-01 BLAST + D0.20 §4 + P-CS-01; pointer W19/CS-02
- [ ] Zero runtime / deploy

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W19+ plików; brak Dowódca `[x]`
- **Smoke:** otwórz W18 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Re-implement CS w tej sesji
- Gate D / secrets / helpdesk merge

## Estimate

≤1 sesja docs + `/handoff`.
