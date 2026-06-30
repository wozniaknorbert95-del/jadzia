# DEPLOY gates preflight — 2026-06-26

**Gates:** DEPLOY-01, DEPLOY-03

## jadzia VPS

| Check | Result |
|-------|--------|
| systemctl jadzia | active |
| worker/health | healthy |
| orders | only `SMOKE-1` |
| env keys | JWT_SECRET, WC_WEBHOOK_SECRET, LEADS_API_KEY |
| GA4 env | not set |
| secrets dir | missing |
| google-analytics-data pip | **missing** on VPS |

## zzpackage

| Check | Result |
|-------|--------|
| FG_JADZIA_WEBHOOK_* | defined |
| FG_JADZIA_LEADS_* | defined |
| mollie-payments-for-woocommerce | active 8.1.7 |
| test_mode_enabled | **no** (prod) |
| FG Jadzia logs | none recent |

## Local tooling

| Tool | Result |
|------|--------|
| gcloud | not installed |
| analytics MCP | ADC not configured |

## Decision

- **DEPLOY-01:** wp-cli synthetic WC order + `processing` status (Mollie test mode OFF; avoids prod charge)
- **DEPLOY-03:** deploy jadzia with `google-analytics-data`; need GA4 SA — search alternate creds or create via Google Cloud if ADC becomes available
