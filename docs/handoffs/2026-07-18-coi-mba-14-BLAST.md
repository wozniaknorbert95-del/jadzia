# BLAST — COI-MBA-14 (W21 Delegat escalation micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-14` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Tydz. 21 = drill eskalacji Delegat (TG + SMTP). Lekcja = D0.9 + SMTP-01 CLOSED — nie nowy smoke / nie sekrety w git.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | Autonomiczny NEXT_COMMAND z handoff W20 |
| Value | Mikro-lekcja: timeline SLA → TG → email Delegat |
| SoT | D0.9 + COI-CMD-SMTP-01 CLOSE + SMTP playbook |
| Spine | tydz. 21 |
| Baseline tip | `2386b47` (+ lokalne W10–W20 uncommitted) |

## L — Limits (1-1-1)

- **Jedna** mikro-lekcja: `W21` Delegat escalation.
- **Nie** generować W22–W52.
- **Nie** zaznaczać kolumny **Dowódca**.
- **Nie** Gate D / Mollie / sekrety w repo / `_mint_*`.
- **Nie** runtime / deploy / świeży SMTP smoke w tej sesji.

## A — Actions

- [ ] `todo.json`: add `COI-MBA-14` → completed
- [ ] `docs/learning/weeks/W21-delegat-escalation.md`
- [ ] Spine: COI-MBA-14; tydz. 21 Agent `[x]`; Dowódca `[ ]`
- [ ] `AGENTS.md` + session handoff
- [ ] CLOSE + `/handoff` (NEXT_COMMAND dla autonomii)

## S — DoD

- [ ] Jeden week file `W21-delegat-escalation.md`
- [ ] Spine tydz. 21 Agent `[x]`, Dowódca nietknięty
- [ ] Linki D0.9 + SMTP-01 CLOSE + playbook
- [ ] Zero secrets / VPS smoke

## STOP

- Fałszywy Dowódca PASS
- Commit SMTP password
- Gate D / secrets dump

## Estimate

≤1 sesja docs + `/handoff`.
