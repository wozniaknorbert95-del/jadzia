# K8 — Demand Desk accessibility budget

Target: axe-core Critical = 0, Serious = 0 on `#view-demand-desk`.

## Automated gates
- Hidden views must use `inert` + `aria-hidden="true"` (see `showView` + initial HTML)
- Keyboard: all `.desk-act-btn` focusable when enabled; Escape closes confirm modal
- Allowlist file: `tests/fixtures/desk_axe_allowlist.json` (empty by default)
- Smoke: `python tools/desk_a11y_smoke.py` (SKIP if Playwright missing; FAIL on Critical/Serious)

## Manual (after deploy GO)
- [ ] axe DevTools desktop scan attached
- [ ] axe DevTools 375 scan attached
- [ ] Tab order: robota → HITL → hunt → KPIs → footer actions
