# VF-VHQ-W2-MISSION-CONTROL — PRECLOSE

**Date:** 2026-07-27  
**Gate:** `VF-VHQ-W2-MISSION-CONTROL` · `in_progress`  
**Cache:** `vhq-w02a`  
**Local URL:** `http://127.0.0.1:8765/index.html?v=vhq-w02a`  
**Founder D1–D7:** approved · Phase B implemented  
**Status:** READY FOR FOUNDER DOGFOOD — **not closed, not committed, not deployed**

---

## 1. Default experience flow

1. Open Commander (`?v=vhq-w02a`)  
2. Cold-open → **Virtual HQ → Mission Control Command View**  
3. Without JWT: session banner + **Sign in** focused (no fake KPI)  
4. Director Brief shows relocated ops rail / priorities / queue  
5. Approval Vault strip PARTIAL → Audyt  
6. Department Pulse (8) + Operations Flow (Sales→Wizard→Order PARKED)  
7. Room Work Views via Pulse / teleport / floors  
8. **Operations Console** / **Sign in** / Esc → Console (auth reachable)

---

## 2. Moved vs remained in Operations Console

| Moved into HQ (canonical mounts) | Remains in Operations Console |
|----------------------------------|-------------------------------|
| `#home-ops-rail` (+ summary/chips) | Auth JWT panel (chrome) |
| `#priorities` (+ heading) | Virtual HQ re-entry CTA |
| `#queue-list` (+ heading) | System map |
| `#cs-followup-form` (Sales Work View) | Truth Cards appendix |
| | Settings / 5 tabs / Marketing / Analytics / Agents / Audit |

Home hero demoted to **Operations Console**. Functions not deleted.

---

## 3. Canonical location table

| Node | Home slot | Mount @ MC | Mount @ Sales | On HQ close |
|------|-----------|------------|---------------|-------------|
| Ops rail | `#vhq-home-slot-ops` | `#vhq-mount-ops` | — | restored |
| Priorities | `#vhq-home-slot-priorities` | `#vhq-mount-priorities` | — | restored |
| Queue | `#vhq-home-slot-queue` | `#vhq-mount-queue` | `#vhq-mount-work-queue` | restored |
| CS form | `#vhq-home-slot-cs` | — | `#vhq-mount-work-cs` | restored |

One mount at a time — **no clones**.

---

## 4. No-JWT / loading behavior

- Banner: `Session required — Sign in / Open Operations Console…`  
- Sign in visible + initial focus  
- Ops summary may show static „Ładowanie ops…” until `/worker/health` (no JWT gate on that fetch)  
- Priorities/queue empty — **no invented cards**  
- With JWT + `loadHome`: `aria-busy` → `Loading company data…` then clear  

---

## 5. Director Brief result

- Relocated real `#priorities`, `#queue-list`, `#home-ops-rail`  
- Copy: priorities display-only; queue = canonical disposition  
- SSH DEGRADED remains visible via ops chips / Agent Ops room (EV-W2-011) when health loads  

---

## 6. Department Pulse + Operations Flow

- Pulse: MC, Sales, Wizard, Agent Ops, Compliance, Finance, Marketing, Orders — status + EV-* + Go to room  
- Flow: **Sales LIVE → Wizard LIVE → Order Desk PARKED** with break explanation  

---

## 7. Regression tests (local CDP)

| Test | Result |
|------|--------|
| no JWT/session | PASS (banner + Sign in) |
| cold-open HQ→MC | PASS |
| Operations Console / auth | PASS (Sign in → `#jwt-input`) |
| MC priorities/queue mounts | PASS |
| Sales Work View queue+CS | PASS |
| Agent Operations DEGRADED | PASS |
| Floor P1 no auto-open + restore slots | PASS |
| Esc → Console + `#vhq-enter` | PASS |
| 5 bottom tabs | PASS |
| DOM restore path | PASS |
| queue disposition / CS / ticket / JWT session | not exercised live (no token in dogfood host) — code paths preserved via same IDs |

---

## 8. Files changed

- `commander-ui/index.html`  
- `commander-ui/styles.css`  
- `commander-ui/app.js`  
- `todo.json`  
- `docs/handoffs/2026-07-27-VF-VHQ-W2-MISSION-CONTROL-PRECLOSE.md` (this file)

---

## 9. Git diff (W2 scope)

```
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
todo.json
(+ this PRECLOSE when staged)

~513 insertions / ~48 deletions on the four runtime/todo files
```

MKT + Campus deploy handoffs remain untouched.

---

## 10. Risks / residuals

1. Without JWT, ops summary may still say „Ładowanie ops…” until health returns — honest, not a fake priority.  
2. IDE browser Tab keystroke may not move focus; trap + Sign in focus verified.  
3. Queue disposition / CS not live-tested in this host (no session) — IDs/events unchanged.  
4. Floor browse restores nodes to Console while HQ open (world mode) — intentional.  
5. W1 prod tip still `3487ec0` — W2 local only (`vhq-w02a`).  

---

## 11. Recommendation

**READY FOR FOUNDER DOGFOOD**

No commit · no deploy · no CLOSE · W3 not activated.
