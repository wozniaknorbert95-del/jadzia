# BLAST — COI-MBA-03 (W10 Marketing HITL micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-03` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 10 spine = rytuał Marketing HITL (jeden cykl publish). Lekcja = ścieżka już LIVE (PUBLISH-B + intake + P-MKT-01), nie nowe API.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-03` (handoff W08+W09) |
| Value | Mikro-lekcja: draft → HITL approve → publish → undo 60s |
| SoT spine | `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` tydz. 10 |
| Scorecard | `#4 AI Marketing LIVE` — nie regresować |
| Baseline tip | `2386b47` (W08–W09 committed) |

**Data flow:** Agent mapuje dowody MKT LIVE → pisze `weeks/W10-….md` → spine Agent `[x]` tydz. 10 → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W10` Marketing HITL ritual.
- **Nie** generować W11–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / merge OS / `_mint_*`.
- **Nie** runtime Python / schema / deploy (`standing_go_closeout=false`).

## A — Actions

- [ ] `todo.json`: add `COI-MBA-03` → completed po CLOSE
- [ ] `docs/learning/weeks/W10-marketing-hitl.md`: cel | treść | wdrożenie (linki) | Dowódca pending
- [ ] Spine: status COI-MBA-03; tydz. 10 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff pointers
- [ ] CLOSE + session `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W10-marketing-hitl.md`
- [ ] Spine tydz. 10 Agent `[x]`, Dowódca nietknięty
- [ ] Zero runtime / deploy
- [ ] Linki do PUBLISH-B / intake / P-MKT-01 / scorecard #4

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W11+; brak Dowódca `[x]`
- **Smoke:** otwórz W10 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Live Facebook publish w tej sesji
- Gate D / payment / secrets

## Estimate

≤1 sesja docs + `/handoff`.
