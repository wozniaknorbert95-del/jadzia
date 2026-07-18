# CLOSE — COI-CMD-UX-POLISH-01 (Home enterprise polish)

**Date:** 2026-07-18  
**Gate:** `COI-CMD-UX-POLISH-01` → **completed** (code + local dogfood)  
**Prod tip:** pending GO (`standing_go_closeout=false`)  
**BLAST:** `docs/handoffs/2026-07-18-coi-cmd-ux-polish-01-BLAST.md`

## Shipped

1. **Tokens + button system** — `commander-ui/styles.css` (surfaces, CTA primary/secondary/danger/ghost, spacing, elevation, typography stack).
2. **Home IA chrome** — eyebrow, hero sub, section titles, skeleton loading, PL empty/error states.
3. **CTA hierarchy** — Potwierdź `primary` / Odłóż `secondary` / Zamknij `danger`; disable during API; toast ok/err.
4. **Hops** — map links with label+meta; toast „Otwieram… (sesja zostaje)”.
5. **Fixes from dogfood** — `.undo-bar[hidden]` override; dark inputs (nie biały JWT box).
6. **Cache-bust** — `styles.css?v=polish01b`, `app.js?v=polish01`.

## Dogfood evidence (local `http://127.0.0.1:8766`)

| Check | Result |
|-------|--------|
| Cold-open eyebrow + titles | PASS |
| Undo bar hidden until used | PASS |
| Hop toast VCMS | `Otwieram: VCMS (sesja Commander zostaje)` · `toast-ok` |
| Primary CTA height | 44px |
| Cache-bust polish01b / polish01 | PASS |
| Checklist POLISH P1–P6 | PASS → `UX-DOGFOOD-PHONE.md` |

Live disposition + prod tip: **po GO deploy**.

## PARK (nietknięte)

Gate D · Mollie · mint/recover · OS merge · MBA regen · VPS bez GO

## NEXT

1. Human **GO** → deploy Commander UI → tip SoT  
2. `/vibe-init` → `COI-CMD-OPS-GUIDE-01` (flex-vcms `docs/study/` handbook, 5 scenariuszy z dogfood)

```text
HANDOFF_FILE: docs/handoffs/2026-07-18-coi-cmd-ux-polish-01-CLOSE.md
BACKLOG_ID: COI-CMD-UX-POLISH-01
STATE: completed local; awaiting GO for prod tip
```
