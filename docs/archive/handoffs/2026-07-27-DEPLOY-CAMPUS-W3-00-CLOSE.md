---
status: "[CLOSED]"
title: "DEPLOY-CAMPUS-W3-00 — Truth Cards LIVE on VPS"
updated: "2026-07-27"
gate: "DEPLOY-CAMPUS-W3-00"
prod_tip: "3487ec0"
cache_asset: "campus-w03b"
cache_url: "campus-w03"
commit: "3487ec0b9f64baf463555c600c45794e3c61a608"
rollback: "df3d59a"
w4_started: false
deploy_evidence_committed: false
---

# Handoff — 2026-07-27 — DEPLOY-CAMPUS-W3-00

## Verdict

**DEPLOY PASS**

## Sequence

| Step | Result |
|------|--------|
| Commit W3 | **`3487ec0`** `feat(campus): add W3 truth cards` |
| Pre-deploy HEAD | `3487ec0b9f64baf463555c600c45794e3c61a608` |
| Dirty tree excluded | MKT materials + W2 deploy handoff (untouched) |
| Push `origin/master` | `df3d59a..3487ec0` |
| VPS pre tip | **`df3d59a`** |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`3487ec0`** |
| `systemctl restart jadzia` | **active** |
| Local `/health` | OK (`Strona OK`) |
| Prod verify `?v=campus-w03` | **PASS** |
| W4 / active_gate change | **not started / not modified** |
| MKT / Ads | **none** |

## Cache tokens (from committed `commander-ui/index.html`)

| Role | Token |
|------|-------|
| Asset bust (`styles.css` / `app.js`) | **`campus-w03b`** |
| Public smoke / SoT URL query | **`campus-w03`** |

Production URL:

```text
https://api.zzpackage.flexgrafik.nl/commander/?v=campus-w03
```

Assets resolve with `?v=campus-w03b` inside HTML.

## Deploy plan (executed)

| Item | Value |
|------|-------|
| Release SHA | `3487ec0b9f64baf463555c600c45794e3c61a608` |
| Cache asset token | `campus-w03b` |
| Rollback SHA | `df3d59a` |
| Expected URL | `https://api.zzpackage.flexgrafik.nl/commander/?v=campus-w03` |
| Smoke | 5 Truth Cards · 5 tabs · no 6th Campus tab · no fake finance KPI · CTAs live · mobile CSS F5 |

## Backup / rollback

| Item | Result |
|------|--------|
| Pre-pull tip recorded | `df3d59a` |
| DB copy backup | `/opt/jadzia/data/jadzia-pre-campus-w3-20260727-172300.db` (post-pull `cp -a`; sqlite3 `.backup` quoting failed over SSH) |
| Rollback readiness | **READY** — `cd /opt/jadzia && git checkout df3d59a && systemctl restart jadzia` then verify `?v=campus-w01` |

## Production verification

**Timestamp:** `2026-07-27T15:21:54Z`  
**Final URL:** https://api.zzpackage.flexgrafik.nl/commander/?v=campus-w03  
**Deployed SHA:** `3487ec0` (`3487ec0b9f64baf463555c600c45794e3c61a608`)

| Check | Result | Evidence |
|-------|--------|----------|
| HTTP Commander | **200** | public GET |
| Asset token `campus-w03b` | **PASS** | `styles.css?v=campus-w03b` + `app.js?v=campus-w03b` in HTML |
| `#truth-cards-pilot` | **PASS** | present · 5× `<article class="truth-card">` |
| Mission Control | **LIVE** | EV-W2-001 · last_verified 2026-07-27T14:22:43Z |
| Sales / Wizard | **LIVE** + SoT | EV-W2-005 · SoT `https://zzpackage.flexgrafik.nl/wizard/` · link HTTP 200 |
| Marketing Studio | **UNVERIFIED** | EV-W3-001 · “campaign state not verified” · 2026-07-27T15:13:35Z |
| Order Desk | **PARKED** | EV-W2-010 · SoT: no live desk |
| Finance / Analytics | **UNVERIFIED** | EV-W2-008 · KPI `insufficient_data` only |
| Exactly 5 bottom tabs | **PASS** | Start · Marketing · Analityka · Agenci · Ustawienia |
| No 6th Campus tab | **PASS** | no Campus nav tab |
| No fake finance KPI | **PASS** | finance card = insufficient_data; €199 = checkout rule text only |
| Dead links (Truth Card CTAs) | **PASS** | Wizard 200 · Commander 200 · styles/app 200 |
| Mobile CTA vs bottom-nav | **PASS (CSS)** | F5: `#truth-cards-pilot` padding-bottom + `scroll-margin-bottom` on `.truth-card__cta` LIVE in `styles.css?v=campus-w03b` |
| MKT / Ads action | **NONE** | no Ads Manager / paid actions |
| `/worker/health` | **degraded** | `ssh_connection=error` · pre-existing INC-SSH-RECOVERY-00 (did not block UI tip sync) |

## Residual risks

1. **SSH DEGRADED** — worker health `ssh_connection=error` (INC-SSH-RECOVERY-00); UI deploy succeeded anyway.
2. **SQLite `.backup` via SSH quoting** — used `cp -a` post-pull; prefer native `.backup` on next runtime deploy.
3. **Mobile touch dogfood** — CSS anti-intercept markers verified; Founder thumb-test on device still recommended.
4. **Marketing UNVERIFIED** — no campaign SoT in Campus freeze; do not treat map “NO ACTIVE CAMPAIGN” as campaign proof.
5. **Local dirty residuals** (not deployed): MKT paths + `DEPLOY-CAMPUS-W2-STATUS-CLOSE.md` handoff.

## Explicit non-actions

- No W4 activation
- No `active_gate` change in this deploy
- No commit of this deploy evidence file
- No MKT file staging / modify / delete
- No Ads / Mollie / Gate D

## Recommended next Founder decision (HITL)

```text
Dogfood prod: https://api.zzpackage.flexgrafik.nl/commander/?v=campus-w03
Then (separate GO only): GO VF-CAMPUS-W4
```

Optional: commit this handoff in a docs-only tip sync later.
