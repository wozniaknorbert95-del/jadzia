# BLAST — COI-CMD-MOBILE-02 Plan3 Control Surface

**Date:** 2026-07-18  
**Repo:** jadzia-core ONLY  
**Branch:** `master` @ `89fd9d0`  
**Backlog:** `COI-CMD-MOBILE-02`  
**Fundacja:** Plan1+2 LIVE; Demand-04 LIVE; `docs/handoffs/2026-07-18-pre-feature-VERIFY.md`  
**Status:** BLAST anchored — **/implement** (enterprise harden: **no JWT in URL**)

## B — Background

MOBILE-01 dał phone hub (bottom nav + system map), ale **sesja JWT nadal wymaga laptopa** (`scripts/jwt_token.py` → paste w `#jwt-input`).  
Ticket deeplink HMAC ≠ Bearer JWT → Home / Ack `sales_cta` pada bez tokenu.  
Brak PWA (manifest/SW) → słaba ścieżka „ikona na telefonie”.

**User value:** Telegram → link → `/commander/` standalone → Home → Ack `sales_cta` (jan/bob) **bez laptopa**.

**Enterprise decision (vs rushed JWT-in-query):** one-time opaque `code` (15 min, single-use) → `POST /auth/exchange` → session JWT in `localStorage` only. JWT never in URL/history/referrer.

**Flow:**
```text
TG /commander (whitelist)
  → mint one-time code (hash in SQLite)
  → send https://api…/commander/?code=<opaque>
commander-ui
  → POST /api/v1/commander/auth/exchange {code}
  → localStorage coi_commander_jwt; history.replaceState strip code
  → loadHome() + disposition (queue:act)
PWA
  → manifest.webmanifest + sw.js (shell cache only; never /api/)
  → installable / standalone
```

## L — Limits

- **No** Gate D / Mollie / min199 / live charge
- **No** Agent OS merge; no rewrite Marketing/Analytics
- **No** park deletes; no ship `_recover_*.py`
- **No** full SSO / OAuth product; no ROLE_SCOPES redesign
- TG `/commander` for existing Telegram whitelist users
- Login **code** TTL **15 min**, single-use; session JWT default **24h** (max 7d)
- Never log full JWT or raw code; SW never caches `/api/`
- Deploy only after Dowódca GO
- ADR D0.6 hub-not-merge stays law

**Security:** opaque code → exchange; HS256 session JWT; strip `code` from URL; paste JWT remains fallback.  
**Perf:** static shell cache only — no offline API fantasy.

## A — Actions (implement checklist)

- [x] `agent/commander/session_login.py` — mint code + exchange → JWT
- [x] `agent/db.py` — `commander_login_codes` table
- [x] `api/routes/commander.py` — `POST /api/v1/commander/auth/exchange`
- [x] `api/telegram.py` — `/commander` (+ `/jwt`)
- [x] `commander-ui` — bootstrap `?code=`, logout, manifest, SW, icons
- [x] Tests: `tests/unit/test_commander_session_login.py`
- [ ] Dogfood LIVE (post-GO): phone → TG → Ack sales_cta
- [ ] CLOSE + deploy GO

## S — Success (DoD)

- [x] One-time code exchange (unit + HTTP)
- [x] TG parse `/commander`
- [x] PWA shell assets present
- [ ] LIVE phone dogfood (post deploy)
- [ ] Parks / Gate D untouched

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
