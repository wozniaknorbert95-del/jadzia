# VF-VHQ-W1-SHELL POLISH — Pre-Close Report

**Date:** 2026-07-27  
**Gate:** `VF-VHQ-W1-SHELL` (unchanged — polish only)  
**Cache:** `vhq-w01b`  
**Local URL:** `http://127.0.0.1:8765/index.html?v=vhq-w01b`  
**Status:** ready for Founder visual re-approval (HITL) — **not closed, not committed, not deployed**

## Scope (done)

Polish only — no new rooms / APIs / data / actions / tabs / backend / 3D / W2.

| # | Issue | Fix |
|---|--------|-----|
| 1 | Floor auto-opened first room | Floor click → `vhqSelectFloor` filter only; browse panel “Select a room on this floor.” MC default **only** on initial HQ entry |
| 2 | Commander background distracting | Opaque `#080b10` shell + `inert`/`aria-hidden` + `visibility:hidden` on backdrop siblings |
| 3 | Soft focus / Tab leaked | Focus trap (`Tab`/`Shift+Tab` cycle), `focusin` guard, Esc closes, Close/`Esc` → focus `#vhq-enter` |

## Files touched

- `commander-ui/app.js` — floor browse, focus trap, inert backdrop, `aria-current` remove (not `"false"`)
- `commander-ui/styles.css` — opaque shell + backdrop inert hide
- `commander-ui/index.html` — teleport placeholder option, cache `vhq-w01b`, hint text

## Dogfood A–J (re-run PASS)

| Step | Result |
|------|--------|
| A Home | PASS |
| B Enter Virtual HQ | PASS → MC |
| C Find MC <5s | PASS |
| D Sales → queue | PASS |
| E Return HQ | PASS → MC |
| F Wizard real URL | PASS `https://zzpackage.flexgrafik.nl/wizard/` |
| G Agent Ops SSH DEGRADED | PASS |
| H Order Desk PARKED | PASS |
| I Esc → `#vhq-enter` | PASS (`inert` cleared) |
| J Keyboard + mobile | PASS (trap + mobile list) |

**P1 floor check:** click P1 → rooms visible, panel `Floor P1` / `select a room`, **Reception NOT auto-opened**. PASS.

## Focus trap evidence (CDP)

- Focusable in open dialog: 12–14 controls (teleport → MC → Close → floors → visible rooms only)
- Tab wrap last→first: `design-studio` → `vhq-teleport`
- Shift+Tab wrap first→last: `vhq-teleport` → `design-studio`
- Backdrop: `inert` count 7 while open; 0 after Esc
- Overlay bg: `rgb(8, 11, 16)`; backdrop siblings `visibility: hidden`
- Note: IDE browser native Tab keystroke does not move focus in this host; trap verified via `vhqTrapTab` + `focusin` guard + inert

## Screenshots

`C:\Users\FlexGrafik\AppData\Local\Temp\cursor\screenshots\`

| File | Proof |
|------|--------|
| `vhq-w1-polish-01-hq-opaque.png` | Opaque HQ / MC (no Commander bleed) |
| `vhq-w1-polish-02-p1-floor-no-autoopen.png` | P1 browse — no Reception auto-open |
| `vhq-w1-polish-03-mobile-room-list.png` | Mobile room-list |
| `vhq-w1-polish-04-focus-close.png` | Dialog dominant + Close in chrome |

## Residual (non-blocking)

- Native Tab in Cursor IDE browser host may not synthesize focus moves; production Chromium/desktop browsers use standard Tab + trap handlers.
- Floor re-click on the **same** floor as the selected room keeps that room (intentional).

## Recommendation

**READY FOR FOUNDER VISUAL APPROVAL** (polish)

## Explicit non-actions

- No commit  
- No deploy  
- No `active_gate` change  
- No W2 start  
- No CLOSE until Founder HITL
