---
status: "[CLOSED]"
title: "DEPLOY-VHQ-W3.2 — Console Cleanup LIVE"
updated: "2026-07-27"
gate: "DEPLOY-VHQ-W3.2"
prod_tip: "de08060"
runtime_commit: "de08060"
cache_asset: "vhq-w32a"
cache_url: "vhq-w32a"
commit: "de08060858d220e496c8b78c666809bfe82f683c"
rollback: "b23bf97"
rollback_cache: "vhq-w31b"
w4_started: false
deploy_evidence_committed: false
---

# Handoff — 2026-07-27 — DEPLOY-VHQ-W3.2

## Verdict

**DEPLOY PASS** + **PRODUCTION DOGFOOD PASS**

## Sequence

| Step | Result |
|------|--------|
| W3.2 CLOSE | DONE (Founder GO) |
| COMMIT W3.2 ONLY | **`de08060`** `feat(vhq): console cleanup — VHQ_ROOMS sole SoT (W3.2)` |
| Push `origin/master` | `b23bf97..de08060` |
| VPS pre tip | **`b23bf97`** |
| VPS backup | `/opt/jadzia/data/jadzia-pre-vhq-w32-20260727-202032.db` |
| VPS `git pull --ff-only` | TIP_MATCH=OK → **`de08060`** |
| `systemctl restart jadzia` | **active** |
| Local `/health` | OK (`Strona OK`) |
| `/worker/health` | **degraded** SSH (pre-existing; did not block UI deploy) |
| Prod verify `?v=vhq-w32a` | **PASS** (primary + console + legacy) |
| W4 | **not started** |
| MKT / Ads / Mollie | **none** |

## Cache token

| Role | Token |
|------|-------|
| Asset bust + public URL query | **`vhq-w32a`** |

```text
Primary: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w32a
Console: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w32a&vhq=console
Legacy:  https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w32a&vhq_shell=legacy
```

## Rollback

| Item | Value |
|------|-------|
| Rollback SHA | `b23bf97` |
| Rollback cache | `vhq-w31b` |
| Soft rollback | `?v=vhq-w32a&vhq_shell=legacy` |
| Hard rollback | `cd /opt/jadzia && git checkout b23bf97 && systemctl restart jadzia` then `?v=vhq-w31b` |

## Production dogfood (A–L condensed)

| Check | Result |
|-------|--------|
| HQ primary cold-open MC · cache `vhq-w32a` | **PASS** |
| Console secondary · Return to HQ first | **PASS** |
| Technical / Evidence + Legacy hosts collapsed default | **PASS** |
| Marketing UNVERIFIED · EV-W3-001 (Pulse + Settings + Truth) | **PASS** |
| Sales LIVE EV-W2-007 · Order PARKED EV-W2-010 | **PASS** |
| SSH DEGRADED EV-W2-011 | **PASS** |
| One `#queue-list` · 5 tabs | **PASS** |
| Sign in → Console JWT focus · Ticket awaryjny | **PASS** |
| `vhqManifestPropagationTest()` 5/5 · no `VHQ_PULSE` | **PASS** |
| Legacy `vhq_shell=legacy` | **PASS** |
| No Ads execute from HQ/Console | **PASS** |

Evidence screenshots (uncommitted):

- `docs/handoffs/evidence-vhq-w32-prod-dogfood/prod-w32-01-primary-mc.png`
- `docs/handoffs/evidence-vhq-w32-prod-dogfood/prod-w32-02-console-default.png`
- `docs/handoffs/evidence-vhq-w32-prod-dogfood/prod-w32-03-legacy-rollback.png`

## Residuals (unchanged)

- Finance / Marketing UNVERIFIED
- SSH degraded (INC-SSH-RECOVERY-00)
- Order / Production not implemented
- Ops priorities/queue need JWT
- Floor cards status-only (intentional)

## W4

**PARKED.** Activate only with explicit Founder GO after this LIVE tip is accepted.

---

**STOP — HITL.** Deploy evidence handoff local-only until Founder stages it. MKT untouched.
