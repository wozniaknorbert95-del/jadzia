---
status: "[CLOSED]"
title: "DEPLOY-VHQ-W2-00 — Virtual HQ W1 Shell + W2 Mission Control LIVE"
updated: "2026-07-27"
gate: "DEPLOY-VHQ-W2-00"
prod_tip: "db32212"
runtime_commit: "4545c6e"
cache_asset: "vhq-w02b"
cache_url: "vhq-w02b"
commit: "db322128faefdd38dda94bce94fadc4360cb7bf5"
rollback: "3487ec0"
w3_started: false
deploy_evidence_committed: false
---

# Handoff — 2026-07-27 — DEPLOY-VHQ-W2-00

## Verdict

**DEPLOY PASS**

## Sequence

| Step | Result |
|------|--------|
| Release tip | **`db32212`** `docs(vhq): close W2 mission control` |
| Runtime ancestor | **`4545c6e`** `feat(vhq): add W2 mission control command view` (ancestor OK) |
| Pre-deploy HEAD local | `db32212` |
| Dirty tree excluded | MKT materials + old Campus deploy handoffs (untouched) |
| Push `origin/master` | `3487ec0..db32212` |
| VPS pre tip | **`3487ec0`** |
| VPS backup | `/opt/jadzia/data/jadzia-pre-vhq-w2-20260727-184439.db` (`cp -a`) |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`db32212`** |
| `systemctl restart jadzia` | **active** |
| Local `/health` | OK (`Strona OK`) |
| Prod verify `?v=vhq-w02b` | **PASS** |
| W3 / active_gate change | **not started / not modified** (`active_gate=""`, W3 parked, `proposed_next_gate_active=false`) |
| MKT / Ads / Mollie | **none** |

## Cache token (from committed `commander-ui/index.html`)

| Role | Token |
|------|-------|
| Asset bust (`styles.css` / `app.js`) + public URL query | **`vhq-w02b`** |

Production URL:

```text
https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w02b
```

## Deploy plan (executed)

| Item | Value |
|------|-------|
| Release SHA | `db322128faefdd38dda94bce94fadc4360cb7bf5` |
| Runtime SHA | `4545c6e` |
| Cache token | `vhq-w02b` |
| Rollback SHA | `3487ec0` |
| Expected URL | `https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w02b` |
| Method | Zasada 11 GO → push → VPS backup → `ff-only` pull → restart → browser/HTTP verify |

## Backup / rollback

| Item | Result |
|------|--------|
| Pre-pull tip recorded | `3487ec0` |
| DB copy backup | `/opt/jadzia/data/jadzia-pre-vhq-w2-20260727-184439.db` |
| Rollback readiness | **READY** — `cd /opt/jadzia && git checkout 3487ec0 && systemctl restart jadzia` then verify `?v=campus-w03` |

## Production verification

**Timestamp:** `2026-07-27T16:44Z` (approx deploy) / verify immediate post-deploy  
**Final URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w02b  
**Deployed SHA:** `db32212` (`db322128faefdd38dda94bce94fadc4360cb7bf5`)

| # | Check | Result | Evidence |
|---|--------|--------|----------|
| 1 | Cold-open → Virtual HQ → Mission Control | **PASS** | Prod browser: HQ open, location `HQ › P3 › Mission Control` |
| 2 | Virtual HQ primary dashboard | **PASS** | Eyebrow “PRIMARY DASHBOARD · COMMANDER = ENGINE”; Console demoted |
| 3 | Operations Console / Sign in reachable | **PASS** | Esc → Console + JWT fallback; “Enter Virtual HQ” + Sign in |
| 4 | No JWT honesty + SSH DEGRADED | **PASS** | Session Required · no fake KPI · EV-W2-011 strip visible |
| 5 | Department Pulse honest statuses | **PASS** | 8 cards: MC/Sales/Wizard LIVE · Agent Ops DEGRADED · Compliance PARTIAL · Finance/Marketing UNVERIFIED · Orders PARKED |
| 6 | Operations Flow Sales→Wizard→Order PARKED | **PASS** | LIVE → LIVE → PARKED · EV-W2-007/005/010 |
| 7 | Work views open | **PASS** | MC · Sales · Wizard · Approval Vault · Agent Operations |
| 8 | Wizard verified URL | **PASS** | `https://zzpackage.flexgrafik.nl/wizard/` HTTP 200 · Work View SoT link |
| 9 | Order Desk PARKED | **PASS** | Room `[PARKED]` · no primary action · EV-W2-010 |
| 10 | Mobile Brief-first / usable | **PASS (CSS+structure)** | `@media (max-width: 600px)` · Navigate HQ drawer · Command View Brief-first; Founder thumb-test still recommended |
| 11 | Keyboard trap / Esc / focus restore | **PASS** | Esc closed HQ → Console; focus restored to Enter Virtual HQ |
| 12 | Exactly five bottom tabs · no sixth | **PASS** | Start · Marketing · Analityka · Agenci · Ustawienia (desktop + bottom-nav) |
| 13 | No MKT / Ads / Mollie / new APIs | **PASS** | UI tip sync only · MKT dirty excluded · no paid/payment actions |
| — | HTTP assets | **PASS** | HTML/CSS/JS `?v=vhq-w02b` → 200 |
| — | `/worker/health` | **degraded** | `ssh_connection=error` · pre-existing INC-SSH-RECOVERY-00 (did not block UI deploy) |

## Residual risks

1. **SSH DEGRADED** — worker `ssh_connection=error` (INC-SSH-RECOVERY-00); static EV-W2-011 shown honestly; live refresh still needs JWT / Agent Ops.
2. **Mobile thumb dogfood** — CSS anti-clutter markers LIVE; Founder device check still recommended.
3. **Ops rail “Ładowanie ops…” without JWT** — expected honesty until session; do not invent priorities.
4. **Local dirty residuals (not deployed):** MKT paths + prior Campus deploy handoffs + this CLOSE file (uncommitted by design).

## Explicit non-actions

- No W3 activation
- No `active_gate` change
- No commit of this deploy evidence file
- No MKT file staging / modify / delete / stash
- No Ads / Mollie / Gate D / new APIs

## Recommended next Founder decision (HITL)

```text
Dogfood prod: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w02b
Then (separate GO only): GO VF-VHQ-W3-ROOMS-COMMERCIAL
```

Optional later: docs-only tip sync to commit this handoff.
