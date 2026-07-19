# BLAST — COI-MBA-01 (spine truth-repair + Week 8 micro-lekcja)

**Date:** 2026-07-18  
**Backlog:** `COI-MBA-01` (NEW)  
**Class:** Feature (docs / learning) — **no runtime code**, no VPS deploy  
**Why:** Po AI OS CLOSEOUT spine nadal pokazuje `[ ]` na gate’ach już `completed` → drift vs scorecard LIVE. Jedna mikro-lekcja odblokowuje rytuał MBA bez generowania Q1–Q4 naraz.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | `/vibe-init` → maintain / MBA spine |
| Value | Honest learning SoT: lekcja = wdrożenie już zrobione + następny mały krok |
| SoT spine | `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md` |
| Scorecard | `#1–9 LIVE` (CLOSEOUT) — nie regresować |

**Data flow:** Agent czyta `todo.json` completed gates + scorecard → aktualizuje spine checkboxes (kolumna agent/wdrożenie) → pisze `docs/learning/weeks/W08-….md` → handoff. Dowódca kolumna zostaje dla human ritual.

## L — Limits (1-1-1)

- **Jedna sesja implement:** (A) truth-repair checkboxów + (B) **jedna** mikro-lekcja `W08` (Knowledge hygiene / KNOW).
- **Nie** generować weeks W09–W52.
- **Nie** zaznaczać kolumny **Dowódca** (human).
- **Nie** Gate D / Mollie / sekrety / merge OS.
- **Nie** runtime Python / schema / deploy (`standing_go_closeout=false`).
- Zakaz G0: nadal obowiązuje — tylko W08.

### Truth-repair map (agent evidence → `[x]` w kolumnie wdrożenia / Gate)

Zaznacz **tylko** gdy `todo` status=`completed` + handoff/scorecard istnieje:

| Tydz | Gate | Evidence |
|------|------|----------|
| 0 | COI-OS-00 | scorecard + KNOW index |
| 1–3 | COI-CMD-UX-01..03 | UX dogfood / completed |
| 4–5 | COI-PROC-00..01 (+02 LIVE) | PROCESS-CATALOG |
| 6 | COI-OPS-AI-00 | OPS-AI scorecard baseline |
| 7 | COI-ROLE-01 | D0.20 |
| 8 | COI-KNOW-00/01 | KNOW mirrors (+ W08 lekcja) |
| 17 | COI-PM-01 | os-api HITL DONE |
| 18–19 | COI-CS-01/02 | CS LIVE |
| 27 | COI-OPS-AI-01 | 60.6% PASS |
| 28 | COI-CMD-MOBILE-02 | PWA foundation LIVE |
| 38 | AI-OS-CLOSEOUT | scorecard #1–9 LIVE |

Week 0 „Dashboard ritual TG” + kolumna Dowódca — **bez zmian** (human).

## A — Actions (implement checklist)

- [ ] `todo.json`: add `COI-MBA-01` `in_progress`; set `active_gate=COI-MBA-01`
- [ ] `docs/learning/AI-MBA-FLEXGRAFIK-SPINE.md`: status note post-CLOSEOUT; apply truth-repair `[x]` per map; leave Dowódca `[ ]`
- [ ] `docs/learning/weeks/W08-knowledge-hygiene.md`: cel | treść mikro | wdrożenie (link KNOW-01 + PROC-02) | Dowódca PASS pending
- [ ] `AGENTS.md`: active_gate / latest blast pointer
- [ ] Handoff CLOSE po implement (nie w tym BLAST)

## S — Success criteria (DoD)

- [ ] Spine nie kłamie vs completed gates (mapa powyżej)
- [ ] Istnieje dokładnie **jeden** nowy plik week: `W08-knowledge-hygiene.md`
- [ ] Kolumna Dowódca nietknięta
- [ ] Zero zmian runtime / deploy
- [ ] `COI-MBA-01` → completed tylko po powyższym + CLOSE handoff

## T — Test plan

- **Unit/Integration:** N/A (docs)
- **Review:** diff spine — żadnego `[x]` bez wiersza w mapie; brak W09+
- **Smoke:** otwórz W08 — linki do KNOW/PROCESS/scorecard resolvują się w repo

## STOP

- Fałszywy Dowódca PASS
- „Catch-up” wszystkich 52 weeks w jednej sesji
- Gate D / payment / secrets

## Estimate

≤1 sesja `/implement` + `/handoff`.
