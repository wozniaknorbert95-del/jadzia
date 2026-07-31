---
status: "[CLOSED]"
title: "DEPLOY-VHQ-P2-SNR-00 — prod PASS"
updated: "2026-07-31"
gate: "DEPLOY-VHQ-P2-SNR-00"
founder_go: "Wiec tak wykonaj deploy…"
prod_tip: "7e34940"
feature_tip: "4c1ab56"
cache_asset: "vhq-w62a"
rollback: "b419b4e"
rollback_cache: "vhq-w61a"
backup: "/opt/jadzia/data/jadzia-pre-p2-snr-20260731.db"
evidence_dir: "docs/handoffs/evidence-vhq-p2-snr-prod/"
---

# DEPLOY-VHQ-P2-SNR-00 — CLOSE

## Verdict

**DEPLOY PASS** + **PROD DOGFOOD PASS** (D3–D6)

## Sequence

| Step | Result |
|------|--------|
| Pre tip | `b419b4e` |
| Backup | `jadzia-pre-p2-snr-20260731.db` |
| Pull | TIP_MATCH → **`7e34940`** |
| Restart jadzia | **active** |
| Health / worker | OK · `ssh_connection=ok` |
| Cache | `vhq-w62a` ×3 in HTML |

## Prod dogfood (`?v=vhq-w62a`)

| DoD | Result |
|-----|--------|
| D3 Decide-now 0 CEO stubs · ≤3 cards | **PASS** — 3 ACTION (fb_post, analytics_stale, sales_cta) |
| D4 STUB hygiene visible | **PASS** — badge + hygiene label |
| D5 Ops not UWAGA from freshness alone | **PASS** — `Ops: OK · data confidence degraded (freshness red)` |
| D6 Real ACTION present | **PASS** |

Evidence: `docs/handoffs/evidence-vhq-p2-snr-prod/prod-w62a-mc.png`

## Residual

- `Analytics stale: GA4` still ACTION in Decide-now → **S4-SNR-FINISH** next

## Rollback

```text
cd /opt/jadzia && git checkout b419b4e && systemctl restart jadzia
# ?v=vhq-w61a
```

DEPLOY_STATUS: **DONE** · TIP: **7e34940** · HEALTH: **OK**
