# BLAST — COI-MBA-09 (W16 Marketing agent depth micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-09` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 16 = głębokość AI Marketing (undo60 + risk matrix drill). Lekcja = D0.20 §2 + D0.8 + CE-05 już w Commander — nie live FB post.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-09` (handoff W15) |
| Value | Mikro-lekcja: public unpublish vs internal 60s; tier risk |
| SoT | D0.8 risk matrix + D0.20 §2 + W10 path |
| Spine | tydz. 16 |
| Baseline tip | `2386b47` (+ lokalne W10–W15 uncommitted) |

**Data flow:** Agent mapuje ROLE mkt + D0.8 → `weeks/W16-….md` → spine Agent `[x]` → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W16` Marketing agent depth.
- **Nie** generować W17–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / `_mint_*`.
- **Nie** runtime / deploy / live Facebook publish.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-09` → completed po CLOSE
- [ ] `docs/learning/weeks/W16-marketing-agent-depth.md`
- [ ] Spine: status COI-MBA-09; tydz. 16 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W16-marketing-agent-depth.md`
- [ ] Spine tydz. 16 Agent `[x]`, Dowódca nietknięty
- [ ] Linki D0.20 + D0.8 + W10 + PUBLISH-B / v3 proof
- [ ] Zero runtime / live publish

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W17+; brak Dowódca `[x]`
- **Smoke:** otwórz W16 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Live FB publish „na zaliczenie”
- Gate D / secrets

## Estimate

≤1 sesja docs + `/handoff`.
