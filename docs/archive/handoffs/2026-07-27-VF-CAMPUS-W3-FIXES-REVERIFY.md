---
status: "[VERIFY PASS · HITL — NOT CLOSED]"
title: "VF-CAMPUS-W3 Pre-Close Fixes + Re-Verify"
gate: "VF-CAMPUS-W3"
updated: "2026-07-27"
fixes: "F1–F7"
ui_paths: "commander-ui/index.html · commander-ui/styles.css"
cache: "campus-w03b"
app_js: unchanged
active_gate_altered: false
commit: false
deploy: false
w3_closed: false
recommendation: "READY FOR FOUNDER CLOSE"
---

# W3 Pre-Close Fixes — Re-Verify

## Recommendation

# READY FOR FOUNDER CLOSE

## F1–F7 applied

| Fix | Result |
|-----|--------|
| F1 Marketing | **UNVERIFIED — campaign state not verified** · `EV-W3-001` · ISO `2026-07-27T15:13:35Z` · no fabricated EV-W2-010 |
| F2 Wizard SoT | Link `https://zzpackage.flexgrafik.nl/wizard/` · LIVE · EV-W2-005 · `noopener noreferrer` |
| F3 Order Desk | PARKED · EV-W2-010 · ISO `2026-07-27T14:26:00Z` · SoT text: *No live source-of-truth / operational desk not implemented* |
| F4 Finance | Renamed **Finance / Analytics** · Finance data UNVERIFIED · EV-W2-008 · no numeric finance KPIs |
| F5 Mobile | Extra shell/truth-card padding + scroll-margin on CTAs · click `#priorities` on 390×844 **no bottom-nav intercept** |
| F6 Contract | All 5 cards: purpose · state · EV · ISO · SoT/honest · action · owner · limitation · insufficient_data |
| F7 Scope | Only `commander-ui/index.html` + `styles.css` for this EXECUTE · MKT untouched |

## DoD checklist (evidence)

| Check | Result | Evidence |
|-------|--------|----------|
| 5 cards | PASS | Mission Control · Sales/Wizard · Marketing Studio · Order Desk · Finance / Analytics |
| Read-only | PASS | no inputs in `#truth-cards-pilot` |
| Explicit states | PASS | LIVE / LIVE / UNVERIFIED / PARKED / UNVERIFIED |
| Evidence IDs | PASS | EV-W2-001 · EV-W2-005 · EV-W3-001 · EV-W2-010 · EV-W2-008 |
| ISO last_verified | PASS | all five `…Z` |
| SoT link or honest no-SoT | PASS | links or explicit no-live SoT |
| Primary / non-action | PASS | |
| Owner | PASS | |
| Limitation | PASS | |
| KPI honesty | PASS | insufficient_data / PARKED freeze · no fake numbers |
| 5 tabs | PASS | Start · Marketing · Analityka · Agenci · Ustawienia |
| app.js | PASS | git diff empty |
| No secrets/PII in links | PASS | |
| Mobile CTA vs bottom-nav | PASS | overlaps=false; browser_click e20 OK on mobile viewport |
| MKT not modified | PASS | ASSET-MATERIALS-PREP / OPERATOR-TODAY / MKT/ unchanged by this EXECUTE |

## Git (this EXECUTE)

**W3 approved paths changed:**
- `commander-ui/index.html`
- `commander-ui/styles.css`

**Untouched MKT / other dirty (excluded):**
- `docs/ops/marketing/ASSET-MATERIALS-PREP.md`
- `docs/ops/marketing/OPERATOR-TODAY.md`
- `docs/ops/marketing/MKT/`
- `docs/handoffs/2026-07-27-MKT-ASSET-00-PROGRESS.md`
- prior `todo.json` / PROGRAM dirty from earlier waves (not part of this fix EXECUTE)

## HITL

W3 **not** closed · **not** committed · **not** deployed · `active_gate` unchanged.  
Next: `CLOSE VF-CAMPUS-W3` → commit (W3 paths only) → deploy.
