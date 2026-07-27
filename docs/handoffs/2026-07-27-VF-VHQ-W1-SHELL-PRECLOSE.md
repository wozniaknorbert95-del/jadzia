---
status: "[PRECLOSE]"
title: "VF-VHQ-W1-SHELL — Virtual HQ shell PRECLOSE"
updated: "2026-07-27"
gate: "VF-VHQ-W1-SHELL"
cache: "vhq-w01"
commit: false
deploy: false
w2_started: false
mkt_touched: false
app_js_changed: true
app_js_reason: "Minimal VHQ shell state: open/close overlay, floor teleport, room panel render, Esc; no API changes; five-tab nav untouched"
---

# Handoff — 2026-07-27 — VF-VHQ-W1-SHELL PRECLOSE

## Verdict

**READY FOR FOUNDER PRECLOSE** (local implementation).  
Virtual HQ shell is an accessible **overlay** inside Commander — not a 6th tab, not a new app, not 3D.

## What was built

| Piece | Implementation |
|-------|----------------|
| Entry | Home `#vhq-entry` · **Enter Virtual HQ** + explore copy |
| Shell | `#vhq-shell` dialog overlay · header · location · Close · Esc |
| Floors | P3/P2/P1/P0/MAG tablist + band map |
| Teleport | `<select id="vhq-teleport">` |
| Room panel | purpose · status · evidence · last_verified · owner · SoT · limitation · 1 primary action |
| Mobile | single-column room list (not tiny building) |
| Cache | `styles.css?v=vhq-w01` · `app.js?v=vhq-w01` |

## MVP primary actions (real only)

| Room | Status | Action |
|------|--------|--------|
| Mission Control | LIVE EV-W2-001 | Close HQ → `#priorities` |
| Approval Vault | PARTIAL EV-W2-009 | Close HQ → Audyt view |
| Agent Operations | DEGRADED EV-W2-011 | Shows SSH INC + DA/OS/VCMS · Open Agenci |
| Sales Room | LIVE EV-W2-007 | Close HQ → `#queue-list` |
| Wizard / Quote | LIVE EV-W2-005 | External Wizard URL |

## Honest non-MVP

Finance UNVERIFIED · Marketing UNVERIFIED · Order PARKED (“not implemented”) · Production/Dispatch/Supplier PARKED · Reception/CS/Design/Preflight/Warehouse/Partner PLANNED · Compliance PARTIAL · Knowledge UNVERIFIED · Boardroom PARTIAL.

**No status upgrades in W1.**

## Files changed

- `commander-ui/index.html`
- `commander-ui/styles.css`
- `commander-ui/app.js` (minimal shell only)
- `todo.json`
- this handoff

## Validation

| Check | Result |
|-------|--------|
| `node --check app.js` | **PASS** |
| Entry + shell markers | **PASS** |
| Exactly 5 bottom/desktop tabs | **PASS** |
| Agent Ops SSH DEGRADED + INC | **PASS** |
| Order Desk PARKED copy | **PASS** |
| Truth Cards block untouched | **PASS** (still present) |
| New APIs | **NONE** |
| Deploy / commit | **NONE** |
| W2 | **not started** |

Founder visual dogfood on phone/desktop still required before CLOSE.

## Risks / limitations

1. Prod still tip `3487ec0` until separate deploy GO (shell not LIVE on VPS yet).  
2. Queue/priorities require JWT session.  
3. Approval Vault is path-to-Audyt only (PARTIAL) — not full L2–L4 vault UX (W6).  
4. Command View “7 questions Brief” deferred to **W2**.  
5. Focus trap is soft (Esc + restore focus); full dialog inert not implemented.

## Founder decision required

```text
CLOSE VF-VHQ-W1-SHELL
```
or `FIX UI` / `BLOCK`

Do not auto-start W2. Do not deploy without GO.
