# PLAN-DEPLOY-INT-009 — Analytics GA4 E2E proof

**Status:** PENDING (after DEPLOY-01 gate)  
**Created:** 2026-06-26  
**Parent:** `docs/plans/PLAN-COI-PHASE-A.md`  
**Code:** P1-02 completed (local)

---

## Goal

Prove INT-009 works end-to-end: GA4 Data API → jadzia `GET /api/v1/analytics/snapshot`.

Code is **done**. This plan is **credentials + deploy + verification only**.

---

## Gate criteria (DEPLOY-03 = completed when ALL true)

- [ ] Google Cloud: Analytics Data API enabled
- [ ] Service account JSON on VPS (`GOOGLE_APPLICATION_CREDENTIALS`)
- [ ] SA added as **Viewer** on app + zzpackage GA4 properties
- [ ] `GA4_PROPERTY_ID_APP` + `GA4_PROPERTY_ID_ZZPACKAGE` in `/root/jadzia/.env`
- [ ] jadzia-core deployed with `google-analytics-data` dep
- [ ] JWT curl → `sync_status: success`, both `sources.app` + `sources.zzpackage`
- [ ] Handoff proof: `docs/handoffs/TEMPLATE-deploy-int-009-proof.md` (filled)

---

## Faza 1 — GA4 credentials (~30 min, Dowódca)

| Step | Action |
|------|--------|
| 1 | [Google Cloud Console](https://console.cloud.google.com/) → enable **Google Analytics Data API** |
| 2 | IAM → Service Accounts → Create → JSON key download |
| 3 | GA4 Admin (app property `G-0XN9Z7HS90`) → Property Access → add SA email as **Viewer** |
| 4 | GA4 Admin (zzpackage `G-L23DGTEKCD`) → same |
| 5 | Copy **numeric** Property IDs (Admin → Property settings → Property ID) |

Measurement ID (`G-xxx`) ≠ Property ID (numeric).

---

## Faza 2 — VPS env (~10 min, Dowódca)

```bash
# On VPS — /root/jadzia/.env (append)
GOOGLE_APPLICATION_CREDENTIALS=/root/jadzia/secrets/ga4-service-account.json
GA4_PROPERTY_ID_APP=<numeric>
GA4_PROPERTY_ID_ZZPACKAGE=<numeric>
GA4_CACHE_TTL_SECONDS=900
```

Upload JSON (secure path, not in repo):

```bash
scp ga4-service-account.json root@185.243.54.115:/root/jadzia/secrets/
chmod 600 /root/jadzia/secrets/ga4-service-account.json
```

---

## Faza 3 — Deploy jadzia-core (~20 min, Dowódca)

```bash
cd jadzia-core
./deployment/deploy-to-vps.sh
# On VPS:
systemctl restart jadzia
curl -f http://localhost:8000/worker/health
```

---

## Faza 4 — Smoke snapshot (~5 min, Dowódca)

```bash
TOKEN="<jwt from JWT_SECRET>"
curl -sS -H "Authorization: Bearer $TOKEN" \
  "http://185.243.54.115:8000/api/v1/analytics/snapshot?period=7d"
```

Expected: `sync_status: success`, non-zero or valid metrics in both sources.

Without GA4 env (pre-deploy): `sync_status: degraded`, `errors: ["ga4_not_configured"]` — HTTP 200.

---

## Faza 5 — Close gate

1. Fill proof handoff from `docs/handoffs/TEMPLATE-deploy-int-009-proof.md`
2. `flexgrafik-meta/docs/core/integration-contracts.md` → INT-009 status **LIVE**
3. `todo.json`: DEPLOY-03 → `completed`

---

## Rollback

1. Remove GA4 env vars from `.env`, restart jadzia
2. Endpoint returns `degraded` — no data loss (read-only, no DB writes)

---

## References

- P1-02 handoff: `docs/handoffs/2026-06-26-p1-02-analytics-node.md`
- INT-009 contract: `flexgrafik-meta/docs/core/integration-contracts.md`
