---
status: FAIL
date: 2026-08-03
gate: DEMAND-OS-MARKETING-4-00
surface: Biuro Popytu / COI Commander
url: "https://api.zzpackage.flexgrafik.nl/commander/?view=demand-desk&cb=desk-dash08"
persona: Dowódca · ADHD · phone · ≤60s
verdict: FAIL
---

# Demand Desk UX/UI Audit Report

## Persona lock

**Dowódca / solo CEO · ADHD · telefon między telefonami · PL.**  
Job: „Czy dziś wpychamy ZZP do Wizard — i co blokuje?”  
Nie czyta jargon footera. Nie ufa fałszywej zieleni. First-time-user lens: ON.

## Verdict

# **FAIL**

Hard gates red. Critical honesty + layout bugs. This surface is **not** “operator ready” for a 60s cash decision.

Repair plan is **out of scope** of this document (next step after Dowódca reads this report).

## Hard-gate scorecard

| Gate | Result | Note |
|------|--------|------|
| Console errors | Incomplete / not instrumented | Chrome MCP unavailable; cursor-ide-browser used |
| Console warnings | Incomplete | same |
| Network 5xx | Pass (observed) | `GET …/demand-os/status` → **200** while UI screamed disconnect |
| Network 403/404 auth pages | Pass (observed) | JWT present (`coi_commander_jwt`) |
| Layout collapse | **FAIL · High→Critical on phone** | 375 emulation: content crushed left; large empty black plane |
| axe Critical/Serious | Incomplete | axe not injected this run |
| LCP / CLS / INP | Incomplete | lighthouse/perf not fully run |
| Interaction Manifest | Pass (below) | real clicks + screenshots |

Allowlist: none (no audit-config.yml).

## Executive judgment (surowy)

Prod Desk looks like a **developer console with panic banners**, not a Biuro Popytu for a founder.

1. It shouts **BRAK POŁĄCZENIA** while the API is healthy and the desk is full of data.  
2. It shows **Stan: LIVE** while ops policy is **live_cadence=PARKED** — and UI never surfaces `live_cadence`.  
3. On phone, layout **collapses** into a skinny rail + void.  
4. Primary action for today’s job is buried under form fields / ICP edit; HITL GOTOWY competes with MONEY_CHECK robota.  
5. Footer is agent telemetry (Doctor/Gate/Kontrakt), not human guidance.  
6. Entire VHQ/Marketing/legacy DOM still rides along in the a11y tree — noise factory.

Calling this “gotowe” was wrong. Ops/tool seal ≠ UX ready.

## Findings

### F1 — Sticky false “BRAK POŁĄCZENIA” (Critical)

- **What:** Banner stays visible after successful load. HTML `hidden=true` but CSS forces `display:flex`.
- **Evidence:** Runtime probe: `hiddenAttr:true`, `display:flex`, `visibility:visible`. Screenshots `01-desk-first-paint.png`, `02-desk-phone-375.png`, `03-desk-fullpage-cdp.png`.
- **API truth:** status **200**, `doctor_ok:true`, KPI populated.
- **Suspected code:** [`commander-ui/styles.css`](../commander-ui/styles.css) `#desk-connection-banner { display: flex; }` (≈2346) overrides `[hidden]`. JS: [`commander-ui/app.js`](../commander-ui/app.js) sets `hidden` on success (~5158–5186).
- **Persona impact:** Dowódca stops trusting the desk in 2 seconds. Panic > action.
- **Repro:** Open prod desk with valid JWT → wait for data → red banner still on screen → Inspect: `hidden` attribute present, computed display flex.

### F2 — Stan LIVE vs live_cadence PARKED (Critical · honesty)

- **What:** Header meta shows `Stan: LIVE`. API `diagnostics.live_cadence=PARKED` + note `env GO ≠ unlock`. UI never shows live cadence / unlock state.
- **Evidence:** fetch probe `state:"LIVE"`, `live_cadence:"PARKED"`; DOM `hasStanLive:true`, `hasLiveCadenceParked:false`.
- **Suspected code:** desk header render in `app.js` (state chip); status builder already honest in `commander_status.py` / money narrative — **UI omits it**.
- **Persona impact:** Looks like “we’re live, publish” while cadence is parked. Exactly the lie Dowódca called out.

### F3 — Phone layout collapse (Critical)

- **What:** At 375×812, desk content compresses into a left rail; majority of viewport is empty black. Bottom nav overlaps footer actions (Diagnostyka click intercepted by nav).
- **Evidence:** `02-desk-phone-375.png`; click Diagnostyka → “Click target intercepted” by `.nav-btn`.
- **Suspected code:** `commander-ui/styles.css` demand-desk grid / mobile nav fixed bar; missing safe-area / scroll padding.
- **Persona impact:** Phone is the intended device. Desk unusable between calls.

### F4 — Robota dnia hierarchy broken (High)

- **What:** Design SoT wants one ROBOTA DNIA line first. UI leads with dual panic banners + ICP form + “Zapisz ICP” (weak text button) before clear “do this now” for MONEY_CHECK.
- **Evidence:** first-paint screenshots; robota text present but visually dominated.
- **Suspected:** `index.html` `#view-demand-desk` structure + CSS `.demand-desk-header`.
- **Persona impact:** ADHD 60s fail — too many competing signals.

### F5 — HITL GOTOWY competes with PARKED cadence (High)

- **What:** Multiple `GOTOWY` / `BLOKADA` on validated TT assets while live publish cadence is PARKED. Label says “bez publikacji” only in confirm modal, not on the row.
- **Evidence:** click GOTOWY → modal “Oznaczyć GOTOWY … (bez publikacji)”.
- **Persona impact:** Feels like publish arming; modal saves it, but row CTA still looks operational-live.

### F6 — Dry hunt confirm path unclear / may execute (High)

- **What:** After Dry komentarz + intended Anuluj path, UI showed toast “Hunt dry OK”, hunt target moved READY→SENT, comments sent 3→4.
- **Evidence:** phone screenshot toast; snapshot hunt `ZZP BOUW demo SENT`; quality “Komentarze wysłane: 4”.
- **Suspected:** confirm modal focus / cancel vs confirm race; or cancel still posts.
- **Persona impact:** Fear of accidental side effects even on “dry”.

### F7 — Footer / Diagnostyka is agent-speak (High · product)

- **What:** Footer: `Doctor: OK · Gate: DEMAND-OS-DESK-CONTRACT-00 · Kontrakt: v2.1.1`. Diagnostyka collapsed; `live_cadence` absent.
- **Evidence:** footer HTML probe; details summary only “Diagnostyka (collapsed)”.
- **Persona impact:** Zero help answering “co blokuje kasę?”.

### H8 — MIXED banner OK but drowned (Medium)

- MIXED warning is correct honesty. Undermined by louder false disconnect (F1) and LIVE state (F2).

### H9 — Legacy DOM noise in a11y tree (Medium)

- Snapshot includes VHQ Mission Control, Marketing organic form, Order Desk shells, etc. while “primary” is Demand Desk.
- Suspected: multi-view single-page with `hidden` views still exposed / not inert.
- Persona / AT: screen-reader and cognitive load disaster.

### H10 — Visual language = terminal cosplay (Medium · polish)

- Monospace everywhere, dashed yellow outline (`.demand-desk--fixture`), bracket nav, low-weight primary buttons.
- Against design SoT “stanowisko cash”, reads as SCADA/debug.

### H11 — STL Gorące alarm unreadability (Medium)

- `STL: open=39 · breach=39 · overnight=39` as a dense sentence. No one action CTA above the fold on phone.

## Interaction Manifest

| t (approx UTC+2) | Action | Result |
|------------------|--------|--------|
| 17:01 | Navigate prod desk URL | Shell loads; JWT present |
| 17:01 | First paint screenshot | Red BRAK POŁĄCZENIA + MIXED; loading→data |
| 17:02 | Runtime probe status API | 200 · LIVE state · live_cadence PARKED · doctor_ok |
| 17:02 | Probe connection banner CSS | hidden=true but display:flex |
| 17:03 | Click Ponów | Banner remains; data already loaded |
| 17:03 | Click GOTOWY tt_w32 | Confirm modal (bez publikacji) |
| 17:03 | Anuluj GOTOWY | Modal closed |
| 17:04 | Click Dry komentarz | Confirm dry modal |
| 17:04 | Anuluj / path | Later toast Hunt dry OK · SENT · comments+1 |
| 17:05 | Emulate 375×812 | Mobile nav; layout collapse |
| 17:05 | Screenshot phone | Evidence 02 |
| 17:06 | Click Diagnostyka | Intercepted by bottom nav |
| 17:06 | CDP fullpage capture | Evidence 03 |

## Evidence paths

- [`docs/handoffs/evidence/ux-audit-2026-08-03/01-desk-first-paint.png`](./evidence/ux-audit-2026-08-03/01-desk-first-paint.png)
- [`docs/handoffs/evidence/ux-audit-2026-08-03/02-desk-phone-375.png`](./evidence/ux-audit-2026-08-03/02-desk-phone-375.png)
- [`docs/handoffs/evidence/ux-audit-2026-08-03/03-desk-fullpage-cdp.png`](./evidence/ux-audit-2026-08-03/03-desk-fullpage-cdp.png)

## Scope / limits

- Tool: cursor-ide-browser (Chrome MCP port 9222 unavailable).
- axe / full Lighthouse not completed → a11y/perf gates = Incomplete (do not upgrade verdict; Fail already from F1–F3).
- No code fixes in this phase.

## What this report is NOT

Not a repair backlog. Not a greenwash. Not permission to unlock live P0.

```text
DONE: [interactive UX audit · FAIL · evidence captured]
LEFT: [repair plan after Dowódca ack · axe/perf optional deepen]
RISKS: [false LIVE / false disconnect trains distrust]
NEXT_COMMAND_FOR_NEW_AGENT: [CreatePlan repair from this report · start F1 CSS hidden + F2 live_cadence chip]

---
CURRENT_STAGE: F6-Iterate
RECOMMENDED_NEXT: Demand Desk UX repair plan (post-report)
WHY_NEXT: Ops seal ≠ UI trust; Critical honesty bugs block operator use.
---
```
