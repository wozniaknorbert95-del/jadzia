# BLAST — COI-MBA-08 (W15 Sales agent deep micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-08` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 15 = głębokość kontraktu AI Sprzedawca (CTA SLA + disposition QA). Lekcja = D0.20 + REV-DEMAND LIVE — nie nowe API / nie płatność.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → `/blast COI-MBA-08` (handoff W14) |
| Value | Mikro-lekcja: kontrakt sales, SLA `sales_cta`, QA dyspozycji |
| SoT | `docs/design/coi-commander/specs/D0.20-ai-role-contracts.md` §1 |
| Spine | tydz. 15 |
| Baseline tip | `2386b47` (+ lokalne W10–W14 uncommitted) |

**Data flow:** Agent mapuje ROLE sales + REV-DEMAND-04 → `weeks/W15-….md` → spine Agent `[x]` → CLOSE. Kolumna Dowódca bez zmian.

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W15` Sales agent deep.
- **Nie** generować W16–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety / `_mint_*`.
- **Nie** runtime / deploy / live charge.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-08` → completed po CLOSE
- [ ] `docs/learning/weeks/W15-sales-agent-deep.md`
- [ ] Spine: status COI-MBA-08; tydz. 15 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff`

## S — Success criteria (DoD)

- [ ] Dokładnie jeden nowy week file: `W15-sales-agent-deep.md`
- [ ] Spine tydz. 15 Agent `[x]`, Dowódca nietknięty
- [ ] Linki D0.20 + P-SALES + REV-DEMAND-04 + W09
- [ ] Zero runtime / deploy / payment

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** brak W16+; brak Dowódca `[x]`
- **Smoke:** otwórz W15 — linki resolvują w repo

## STOP

- Fałszywy Dowódca PASS
- Gate D / Mollie LIVE
- Secrets / `_mint_*`

## Estimate

≤1 sesja docs + `/handoff`.
