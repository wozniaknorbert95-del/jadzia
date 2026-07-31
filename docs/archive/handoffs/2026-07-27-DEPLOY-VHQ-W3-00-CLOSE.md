---
status: "[CLOSED]"
title: "DEPLOY-VHQ-W3-00 — Virtual HQ W3 Commercial Rooms LIVE"
updated: "2026-07-27"
gate: "DEPLOY-VHQ-W3-00"
prod_tip: "b237fd5"
runtime_commit: "8727b6b"
cache_asset: "vhq-w03b"
cache_url: "vhq-w03b"
commit: "b237fd572e2924819d545979ae9f494df5a57eaa"
rollback: "db32212"
w4_started: false
deploy_evidence_committed: false
---

# Handoff — 2026-07-27 — DEPLOY-VHQ-W3-00

## Verdict

**DEPLOY PASS**

## Sequence

| Step | Result |
|------|--------|
| Release tip | **`b237fd5`** `docs(vhq): close W3 commercial rooms` |
| Runtime ancestor | **`8727b6b`** `feat(vhq): add W3 commercial room views` (ancestor OK) |
| Pre-deploy HEAD local | `b237fd5` |
| Dirty tree excluded | MKT materials + old Campus/VHQ-W2 deploy handoffs (untouched) |
| Push `origin/master` | `db32212..b237fd5` |
| VPS pre tip | **`db32212`** |
| VPS backup | `/opt/jadzia/data/jadzia-pre-vhq-w3-20260727-190528.db` (`cp -a`) |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`b237fd5`** |
| `systemctl restart jadzia` | **active** |
| Local `/health` | OK (`Strona OK`) |
| Prod verify `?v=vhq-w03b` | **PASS** |
| W4 / `active_gate` change | **not started / not modified** (`active_gate=""`, W4 parked, `proposed_next_gate_active=false`) |
| MKT / Ads / Mollie / new APIs | **none** |

## Cache token (from committed `commander-ui/index.html`)

| Role | Token |
|------|-------|
| Asset bust (`styles.css` / `app.js`) + public URL query | **`vhq-w03b`** |

Production URL:

```text
https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w03b
```

## Deploy plan (executed)

| Item | Value |
|------|-------|
| Release SHA | `b237fd572e2924819d545979ae9f494df5a57eaa` |
| Runtime SHA | `8727b6b` |
| Cache token | `vhq-w03b` |
| Rollback SHA | `db32212` |
| Expected URL | `https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w03b` |
| Method | Zasada 11 GO → push → VPS backup → `ff-only` pull → restart → browser/HTTP verify |

## Backup / rollback

| Item | Result |
|------|--------|
| Pre-pull tip recorded | `db32212` |
| DB copy backup | `/opt/jadzia/data/jadzia-pre-vhq-w3-20260727-190528.db` |
| Rollback readiness | **READY** — `cd /opt/jadzia && git checkout db32212 && systemctl restart jadzia` then verify `?v=vhq-w02b` |

## Production verification

**Timestamp:** `2026-07-27T19:05Z` (deploy) / verify immediate post-deploy  
**Final URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w03b  
**Deployed SHA:** `b237fd5` (`b237fd572e2924819d545979ae9f494df5a57eaa`)

| # | Check | Result | Evidence |
|---|--------|--------|----------|
| 1 | Cold-open → Virtual HQ → Mission Control | **PASS** | Prod browser: HQ open, location `HQ › P3 › Mission Control`, cache `vhq-w03b` |
| 2 | Commercial Floor available | **PASS** | P1 Commercial floorshows Sales / Wizard / Marketing rooms |
| 3 | Sales Room — one canonical queue | **PASS** | Work view: single `Kolejka (CRITICAL + ACTION)` · SoT `#queue-list` · no invented CRM |
| 4 | Sales → Wizard handoff | **PASS** | `Open Wizard / Quote Room` → `HQ › P1 › Wizard / Quote Room` |
| 5 | Wizard Room | **PASS** | SoT `https://zzpackage.flexgrafik.nl/wizard/` (HTTP 200) · KPI `wizard_starts → insufficient_data` · Order Desk handoff `[PARKED]` |
| 6 | Marketing Studio | **PASS** | `UNVERIFIED — campaign state not verified · EV-W3-001` · observe-only (`Open Marketing tab (observe)`) · paid PARKED · no publish / Ads action from room |
| 7 | Marketing status consistent everywhere | **PASS** | Pulse · floor card `[UNVERIFIED]` · room panel · System Map · Settings map · Truth Cards — all EV-W3-001; **no** `NO ACTIVE CAMPAIGN` |
| 8 | Mission Control / Agent Ops / Console | **PASS** | MC Brief LIVE; Agent Ops room DEGRADED honest; Esc → Operations Console |
| 9 | Mobile + keyboard + Esc/focus | **PASS** | Mobile 390×844: `Navigate HQ` + P1 Commercial rooms; Esc closes HQ; focus restored to `#vhq-enter` |
| 10 | Exactly five bottom tabs · no sixth | **PASS** | Start · Marketing · Analityka · Agenci · Ustawienia |
| 11 | No MKT / Ads / Mollie / backend / new APIs | **PASS** | UI tip sync only · MKT dirty excluded · no paid/payment actions from VHQ |
| — | HTTP assets | **PASS** | HTML/CSS/JS `?v=vhq-w03b` → 200 |
| — | `/worker/health` | **degraded** | `ssh_connection=error` · pre-existing INC-SSH-RECOVERY-00 (did not block UI deploy) |

## Residual risks

1. **SSH DEGRADED** — worker `ssh_connection=error` (INC-SSH-RECOVERY-00); static EV-W2-011 shown honestly; live refresh still needs JWT / Agent Ops.
2. **Campaign state remains UNVERIFIED** — EV-W3-001 by design until MKT / Ads Manager HITL outside VHQ.
3. **Ops rail “Ładowanie ops…” without JWT** — expected honesty until session; do not invent priorities.
4. **Local dirty residuals (not deployed):** MKT paths + prior Campus/VHQ-W2 deploy handoffs + this CLOSE file (uncommitted by design).

## Explicit non-actions

- No W4 activation
- No `active_gate` change
- No commit of this deploy evidence file
- No MKT file staging / modify / delete / stash
- No Ads / Mollie / Gate D / new APIs

## Recommended next Founder decision (HITL)

```text
Dogfood prod: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w03b
Then (separate GO only): GO VF-VHQ-W4-ROOMS-OPERATIONS
```

Optional later: docs-only tip sync to commit this handoff.
