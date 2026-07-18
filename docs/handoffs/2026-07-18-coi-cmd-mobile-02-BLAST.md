# BLAST — COI-CMD-MOBILE-02 Plan3 Control Surface

**Date:** 2026-07-18  
**Repo:** jadzia-core ONLY  
**Branch:** `master` @ `89fd9d0`  
**Backlog:** `COI-CMD-MOBILE-02`  
**Fundacja:** Plan1+2 LIVE; Demand-04 LIVE; `docs/handoffs/2026-07-18-pre-feature-VERIFY.md`  
**Status:** BLAST anchored — ready `/implement`

## B — Background

MOBILE-01 dał phone hub (bottom nav + system map), ale **sesja JWT nadal wymaga laptopa** (`scripts/jwt_token.py` → paste w `#jwt-input`).  
Ticket deeplink HMAC ≠ Bearer JWT → Home / Ack `sales_cta` pada bez tokenu.  
Brak PWA (manifest/SW) → słaba ścieżka „ikona na telefonie”.

**User value:** Telegram → link → `/commander/` standalone → Home → Ack `sales_cta` (jan/bob) **bez laptopa**.

**Flow:**
```text
TG /commander (Dowódca only)
  → mint short-lived JWT (role=dowodca, TTL ≤ 24h)
  → send https://api…/commander/?jwt=<token>
commander-ui
  → bootstrap: ?jwt= → localStorage coi_commander_jwt → history.replaceState strip
  → loadHome() + disposition (queue:act)
PWA
  → manifest.webmanifest + sw.js (shell cache only)
  → installable / standalone
```

## L — Limits

- **No** Gate D / Mollie / min199 / live charge
- **No** Agent OS merge; no rewrite Marketing/Analytics
- **No** park deletes; no ship `_recover_*.py`
- **No** full SSO / OAuth product; no ROLE_SCOPES redesign
- TG `/commander` **only** for allowlisted Dowódca chat (existing admin gate)
- JWT TTL short (default **24h**, max 7d); never log full token
- SW caches only shell assets (html/css/js/icons) — **never** API responses
- Deploy only after Dowódca GO
- ADR D0.6 hub-not-merge stays law

**Security:** reuse HS256 + `JWT_SECRET`; scope `queue:act` via role dowodca; strip `jwt` from URL after save; one-time display in TG only.  
**Perf:** static assets only; SW network-first or cache-first for shell — no offline API fantasy.

## A — Actions (implement checklist)

- [ ] `agent/commander/session_jwt.py` (or thin helper) — `mint_commander_session_jwt(sub, role, hours=24)`
- [ ] `api/telegram.py` — command `/commander` (alias `/jwt`): allowlist → mint → send public URL with `?jwt=`
- [ ] `commander-ui/app.js` — parse `?jwt=` / `#jwt=` → `setToken` → strip query; register SW; optional logout clears storage
- [ ] `commander-ui/index.html` — `<link rel="manifest">`, theme-color, apple-touch-icon
- [ ] `commander-ui/manifest.webmanifest` — name FlexGrafik Commander, `start_url=/commander/`, `display=standalone`, icons
- [ ] `commander-ui/sw.js` — precache shell; skip `/api/`
- [ ] Icons — minimal `icon-192.png` / `icon-512.png` (or SVG→PNG one-shot; no brand redesign)
- [ ] Tests: JWT mint helper unit; telegram handler unit (allowlist / reject); UI bootstrap covered lightly if feasible
- [ ] Dogfood checklist in CLOSE: phone → TG link → Ack sales_cta
- [ ] Handoff CLOSE + `todo.json` / brain / AGENTS; await deploy GO

## S — Success (DoD)

- [ ] From phone TG: `/commander` → opens Commander authenticated (Home loads queue)
- [ ] Ack/Snooze/Close `sales_cta` works with scoped JWT (HTTP 200 disposition)
- [ ] Paste panel still works as fallback
- [ ] `manifest` + SW registered; Lighthouse/install prompt path possible (Android Chrome)
- [ ] Ticket deeplink path unchanged
- [ ] No API contract break; parks / Gate D untouched
- [ ] pytest green for new units

## T — Test plan

| Layer | Cases |
|-------|--------|
| Unit | mint JWT decodable with `JWT_SECRET`; TG rejects non-admin; allowlist sends URL containing `/commander/?jwt=` |
| UI smoke | `?jwt=` sets localStorage and strips from address bar |
| Dogfood (post-GO) | Phone: TG → Home → Ack lead #4 or #5 → disposition acked |

## Decision (senior)

**Path:** TG `/commander` short JWT URL + UI bootstrap + PWA stubs in one slice.  
**Why:** paste-from-laptop fails Plan3 goal (“bez laptopa”); PWA alone bez JWT = half product.

```text
BLAST_ANCHOR: docs/handoffs/2026-07-18-coi-cmd-mobile-02-BLAST.md
BACKLOG_ID: COI-CMD-MOBILE-02
INVARIANTS_TO_PROTECT: Gate D, parks, Agent OS merge, Marketing rewrite, _recover_*.py, D0.6 hub-not-merge
SUCCESS_CRITERIA: phone TG→JWT→Home→Ack sales_cta; PWA installable shell; pytest green
IMPLEMENTATION_PLAN: session_jwt helper → telegram /commander → app.js bootstrap → manifest+sw → tests → CLOSE

---
CURRENT_STAGE: L1-Design (BLAST anchored)
RECOMMENDED_NEXT: /implement
WHY_NEXT: Technical contract established; gate already COI-CMD-MOBILE-02
---
```
