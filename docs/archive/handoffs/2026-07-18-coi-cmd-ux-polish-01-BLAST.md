# BLAST — COI-CMD-UX-POLISH-01 (Home enterprise polish)

**Date:** 2026-07-18  
**Backlog:** `COI-CMD-UX-POLISH-01` (NEW)  
**Class:** Feature — Commander UI (static `commander-ui/`)  
**Surface (1-1-1):** **Home only** — nie Marketing, nie mobile JWT  
**Why:** UX-01..03 dały IA/chrome/load; Home nadal wygląda jak „dev shell” (system font, płaskie przyciski, słaba hierarchia CTA). Cel = cold-open na poziomie enterprise ops dashboard.

## B — Background

| Field | Value |
|-------|-------|
| Trigger | Dowódca: enterprise UX + pipeline profesjonalizmu + instrukcja obsługi |
| Value | Dowódca otwiera Start → panuje (kolory, CTA, hops) bez paniki |
| SoT UX | D0.15–D0.19 + `UX-BRIEF-COMMANDER.md` + `UX-DOGFOOD-PHONE.md` |
| Prior | UX-03 dogfood PASS @ tip `2ba7c85` |

**Data flow (no new API):**  
Browser → `commander-ui/index.html` Home → `app.js` (priorities/queue/hops) → existing Commander JWT APIs → DOM.  
Polish = tokens + typography + button/CTA states + hop affordance + empty/loading polish **tylko w `#view-home` (+ shared tokens w `:root` jeśli Home ich używa).**

## L — Limits (1-1-1 + PARK)

- **Jedna surface:** Home (`#view-home` + global tokens/nav active state wpływające na cold-open).
- **Nie** Marketing composer, **nie** JWT mint/login rewrite, **nie** PWA install.
- **Nie** Gate D / Mollie / mint-recover commit / OS↔jadzia merge.
- **Nie** regeneracja MBA W00–W52; **nie** fałszywy Dowódca PASS.
- **Nie** VPS deploy bez GO (`standing_go_closeout=false`).
- **Nie** zmiany Python runtime / schema (chyba że dogfood ujawni regress — wtedy osobny HOTFIX).
- Shared CSS tokens OK; unikać redesignu innych view poza tym, co wynika z `:root`.

### Companion (NIE w tym gate — osobna sesja)

| Gate | Repo | Cel |
|------|------|-----|
| `COI-CMD-OPS-GUIDE-01` | `flex-vcms` | Profesjonalna instrukcja obsługi Commandera → `docs/study/` (scenariusze z dogfood) |

Handbook **po** dogfood Home — scenariusze = evidence, nie fantazja.

## A — Actions (`/implement`)

### A1 Design tokens (enterprise Home)

- [ ] `commander-ui/styles.css`: rozszerz `:root` — surface elevation, border, CTA primary/danger/ghost, success/warn, spacing scale, radius; **bez** purple-glow cliché.
- [ ] Typography: czytelny stack (nie sam `system-ui`); hierarchy H1 Home / meta / body.
- [ ] Button system: `.primary` / secondary / danger / ghost — hover, active, disabled, focus-visible; touch ≥44px zachowane.

### A2 Home interaction polish

- [ ] `commander-ui/index.html` + `app.js`: Home CTA hierarchy (1 primary action na kartę priorytetu); spójne toasty/redirect feedback.
- [ ] Hops (D0.19): wizualnie „enterprise link” — label + stan loading/error bez psucia JWT session.
- [ ] Empty / loading / error Home: skeleton lub spokojny PL copy (D0.17), nie surowy pusty panel.
- [ ] Cache-bust query na `styles.css` / `app.js` w HTML (jak UX-03).

### A3 Evidence

- [ ] Dogfood checklist: rozszerz lub dodaj sekcję POLISH w `docs/design/coi-commander/UX-DOGFOOD-PHONE.md` (Home cold-open + 3 taps).
- [ ] Browser dogfood lokalnie (lub staging URL); screenshot/notes w CLOSE.
- [ ] Tip evidence **po GO deploy** (nie w implement bez GO).

### A4 Backlog / SoT

- [ ] `todo.json`: gate `in_progress` → `completed` po DoD.
- [ ] `AGENTS.md` + `.cursor/session-state.md` + `.cursor/current-task.md`.
- [ ] CLOSE handoff: `docs/handoffs/2026-07-18-coi-cmd-ux-polish-01-CLOSE.md`.

## S — Success criteria (DoD)

- [ ] Home cold-open: czytelna hierarchia (priorytety → CTA → hops), spójna kolorystyka tokenów.
- [ ] Każdy primary button na Home ma jasny feedback (toast / view change / hop).
- [ ] Dogfood Home **PASS** (checklist wypełniony).
- [ ] Tip evidence: lokalny commit SHA; **prod tip dopiero po GO**.
- [ ] Zero Gate D / zero MBA regen / zero mint-recover w commit.
- [ ] `COI-CMD-UX-POLISH-01` → completed + CLOSE.

## T — Test plan

| Layer | What |
|-------|------|
| Unit | N/A UI-static (opcjonalnie istniejące pytest Commander bez zmian kontraktu) |
| Visual | Desktop + 390px: nav 5, touch 44px, contrast CTA |
| Dogfood | Cold-open → ack/close lead LUB empty state → hop VCMS/OS (401 OK) → session JWT survives |
| Smoke | `/health` green; Home ładuje queue bez regresji Content-Type |

## Professionalism pipeline (program — poza 1 surface)

```text
L0  /vibe-init          ← DONE this session
L1  /blast Home         ← THIS ANCHOR
L2  /implement Home     ← next (tokens + CTA + hops polish)
L3  dogfood + CLOSE     ← evidence w jadzia-core
L4  GO → deploy         ← tylko po GO; tip SoT na VPS
──── cut 1-1-1 ────
L1b /blast OPS-GUIDE    ← flex-vcms study handbook (5 scenariuszy z dogfood)
L2b write + link index  ← docs/study/ + NAUKA card
L3b Dowódca walkthrough ← human PASS scenariuszy
```

### 5 scenariuszy handbook (draft — wypełnić po dogfood)

1. **Cold-open dnia** — Start → 3 priorytety → jedna akcja  
2. **Lead hot** — ack / snooze / close + toast  
3. **Marketing hop** — Start → Marketing (osobny gate polish; tu tylko nawigacja)  
4. **Eskalacja / Delegat** — Settings path + SMTP already LIVE  
5. **Emergency no-laptop** — PWA/JWT path (MOBILE-02; bez mint w docs)

## STOP

- Multi-surface redesign w jednej sesji  
- Autonomiczny deploy  
- Gate D / Mollie / secrets  
- MBA week regen  

## Estimate

- `/implement` Home: ≤1 sesja  
- OPS-GUIDE VCMS: ≤1 sesja po CLOSE polish  
- Deploy: human GO  

---

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-coi-cmd-ux-polish-01-BLAST.md
BACKLOG_ID: COI-CMD-UX-POLISH-01
INVARIANTS_TO_PROTECT: JWT session, IA 5 PL nav, D0.18 load budget, Gate D parked, MBA weeks frozen
SUCCESS_CRITERIA: Home enterprise polish + dogfood PASS + tip after GO; zero parks violated
IMPLEMENTATION_PLAN: styles tokens → Home CTA/hops → cache-bust → dogfood → CLOSE → (GO) deploy
```
