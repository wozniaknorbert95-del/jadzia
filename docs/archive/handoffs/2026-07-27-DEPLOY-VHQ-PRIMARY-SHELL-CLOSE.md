---
status: "[CLOSED]"
title: "DEPLOY-VHQ-PRIMARY-SHELL — W3.1 Primary Shell LIVE"
updated: "2026-07-27"
gate: "DEPLOY-VHQ-PRIMARY-SHELL"
prod_tip: "b23bf97"
runtime_commit: "6ed8713"
cache_asset: "vhq-w31b"
cache_url: "vhq-w31b"
commit: "b23bf9731956ce24b02499fa56f0946a238a29ce"
rollback: "b237fd5"
rollback_cache: "vhq-w03b"
w4_started: false
deploy_evidence_committed: false
---

# Handoff — 2026-07-27 — DEPLOY-VHQ-PRIMARY-SHELL

## Verdict

**DEPLOY PASS**

## Sequence

| Step | Result |
|------|--------|
| Release tip | **`b23bf97`** `docs(vhq): close W3.1 primary shell migration` |
| Runtime ancestor | **`6ed8713`** `feat(vhq): make virtual HQ the primary app shell` (ancestor OK) |
| Pre-deploy HEAD local | `b23bf97` |
| Dirty tree excluded | MKT materials + prior Campus/VHQ deploy handoffs (untouched) |
| Push `origin/master` | `b237fd5..b23bf97` |
| VPS pre tip | **`b237fd5`** |
| VPS backup | `/opt/jadzia/data/jadzia-pre-vhq-primary-shell-20260727-195231.db` |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`b23bf97`** |
| `systemctl restart jadzia` | **active** |
| Local `/health` | OK (`Strona OK`) |
| Prod verify `?v=vhq-w31b` | **PASS** (primary + legacy) |
| Post-deploy VPS tip recheck | **`b23bf97`** / `vhq-w31b` in `index.html` |
| W4 / `active_gate` change | **not started / not modified** |
| MKT / Ads / Mollie / new APIs | **none** |

## Cache token (from committed `commander-ui/index.html`)

| Role | Token |
|------|-------|
| Asset bust (`styles.css` / `app.js`) + public URL query | **`vhq-w31b`** |

Production URLs:

```text
Primary: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w31b
Legacy:  https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w31b&vhq_shell=legacy
```

## Deploy plan (executed)

| Item | Value |
|------|-------|
| Release SHA | `b23bf9731956ce24b02499fa56f0946a238a29ce` |
| Runtime SHA | `6ed8713` |
| Cache token | `vhq-w31b` |
| Rollback SHA | `b237fd5` |
| Rollback URL | `https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w03b` |
| Method | Zasada 11 GO → push → VPS backup → `ff-only` pull → restart → browser/HTTP verify |

## Backup / rollback

| Item | Result |
|------|--------|
| Pre-pull tip recorded | `b237fd5` |
| DB copy backup | `/opt/jadzia/data/jadzia-pre-vhq-primary-shell-20260727-195231.db` |
| Rollback readiness | **READY** — `cd /opt/jadzia && git checkout b237fd5 && systemctl restart jadzia` then verify `?v=vhq-w03b` |
| Soft rollback (no checkout) | `?v=vhq-w31b&vhq_shell=legacy` — modal path verified LIVE |

## Production verification

**Timestamp:** `2026-07-27T19:52Z` (deploy) / dogfood complete `~19:55–20:05Z`  
**Deployed SHA:** `b23bf97` (`b23bf9731956ce24b02499fa56f0946a238a29ce`)

### PRIMARY MODE (`?v=vhq-w31b`)

| # | Check | Result | Evidence |
|---|--------|--------|----------|
| 1 | Cold-open → Virtual HQ → Mission Control | **PASS** | Prod: `HQ › P3 › Mission Control` · cache `vhq-w31b` · Start `aria-current` |
| 2 | HQ not dialog / not aria-modal | **PASS** | Primary: `role=null`, `aria-modal=null`, parent `#view-hq`, relative app view |
| 3 | Start tab → Mission Control | **PASS** | Start current · MC Brief visible |
| 4 | Room → Esc → Mission Control | **PASS** | Sales Esc → MC |
| 5 | MC → Esc → Operations Console | **PASS** | Console + Return to HQ |
| 6 | Operations Console → Return to HQ | **PASS** | Return restores HQ / MC |
| 7 | Sign in → Console + JWT focus | **PASS** | `#jwt-input` focused |
| 8 | Browser Back / Forward MC → World → Sales → Console | **PASS** | `pushState` URLs `vhq=mc|world|sales-room|console`; live `history.back` console→sales; popstate apply world/sales/console |
| 9 | One canonical queue only | **PASS** | Single `Kolejka (CRITICAL + ACTION)` · SoT `#queue-list` |
| 10 | Exactly five bottom tabs | **PASS** | Start · Marketing · Analityka · Agenci · Ustawienia |
| 11 | Mobile brief-first | **PASS** | 390×844: Navigate HQ + Director Brief + 5 tabs |
| 12 | Marketing UNVERIFIED / observe-only / no Ads | **PASS** | EV-W3-001 · Hard STOP · paid PARKED · Truth Card observe-only |
| 13 | Order Desk PARKED | **PASS** | EV-W2-010 · pulse + Truth Card |
| 14 | SSH DEGRADED evidence visible | **PASS** | EV-W2-011 · INC-SSH-RECOVERY-00 · `/worker/health` degraded (pre-existing; did not block UI deploy) |

### LEGACY ROLLBACK (`?v=vhq-w31b&vhq_shell=legacy`)

| # | Check | Result | Evidence |
|---|--------|--------|----------|
| 15 | Modal visible, not blank | **PASS** | `#vhq-shell` portaled to `BODY` · `role=dialog` · `aria-modal=true` · MC content visible |
| 16 | Focus trap | **PASS** | Focus inside shell · 7 body siblings `inert` while open |
| 17 | Esc restore + Sign in route | **PASS** | Esc → shell hidden, focus `#vhq-enter`, inert=0; Sign in → `#jwt-input` focus |
| 18 | Return to primary — no lingering inert/dialog | **PASS** | Primary URL: `role=null`, `aria-modal=null`, `vhq-legacy=false`, `inertCount=0`, parent `#view-hq` |

## Residual risks

1. **SSH DEGRADED** — worker `ssh_connection=error` (INC-SSH-RECOVERY-00); static EV-W2-011 shown honestly; live refresh still needs JWT / Agent Ops.
2. **Campaign state remains UNVERIFIED** — EV-W3-001 by design until MKT / Ads Manager HITL outside VHQ.
3. **Ops rail “Ładowanie ops…” without JWT** — expected honesty until session; do not invent priorities.
4. **History stack pollution** — mixed full-document navigations (legacy ↔ primary) in one tab can interleave with SPA `pushState`; clean cold tab is reliable for Founder dogfood.
5. **Local dirty residuals (not deployed):** MKT paths + prior Campus/VHQ deploy handoffs + this CLOSE file (uncommitted by design).

## Explicit non-actions

- No W4 activation
- No `active_gate` change to W4
- No commit of this deploy evidence file
- No MKT file staging / modify / delete / stash
- No Ads / Mollie / Gate D / new APIs

## Recommended next Founder decision (HITL)

```text
1) Dogfood prod primary:
   https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w31b
2) Spot-check legacy soft rollback:
   https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w31b&vhq_shell=legacy
3) Only after Founder acknowledge (separate GO):
   GO VF-VHQ-W4-ROOMS-OPERATIONS
```

Hard rollback if needed: checkout **`b237fd5`** + restart → verify `?v=vhq-w03b`.
