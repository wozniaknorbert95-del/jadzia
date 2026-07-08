# Jadzia COI — Spine Proof Matrix

**Updated:** 2026-07-08  
**VPS:** `185.243.54.115` `/opt/jadzia`  
**Spine target:** 7/7 LIVE capabilities (~85% operational COI)

---

## Summary

| # | Capability | INT | Prod status | Evidence |
|---|------------|-----|-------------|----------|
| 1 | Order intelligence | INT-002 | **PASS** | prod-smoke + orders=31 |
| 2 | Lead unification | INT-004 | **PASS** | DEPLOY-02 handoff + LEADS key configured |
| 3 | GA4 snapshot | INT-009 | **PASS** | prod-smoke analytics/snapshot |
| 4 | Content calendar | INT-010 | **PASS** | prod-smoke list + create |
| 5 | Sales chat widget | INT-001 | **PASS** | route LIVE; widget on zzpackage |
| 6 | WP SSH agent | — | **PASS** | Telegram + worker; SSH ok in health |
| 7 | Worker + HITL | — | **PASS** | JWT worker/health + dashboard |
| 8 | Weekly brief | S3-02 | **CONFIGURED** | `WEEKLY_BRIEF_INTERVAL_SECONDS=604800`; manual verify optional |

**prod-smoke (2026-07-08):** `pass=8 fail=0` · git `@463e5e0` · service `active`

---

## Per-capability proof

### 1. Orders (INT-002)

```bash
# On VPS
bash /opt/jadzia/deployment/prod-smoke.sh   # WC_WEBHOOK_SECRET + real WC order
sqlite3 /opt/jadzia/data/jadzia.db "SELECT COUNT(*) FROM orders;"
```

Handoff: `docs/handoffs/2026-06-26-deploy-int-002-proof.md` (order #3149 + ongoing)

### 2. Leads (INT-004)

```bash
grep -q '^LEADS_API_KEY=' /opt/jadzia/.env && echo OK
```

Handoff: `docs/handoffs/2026-06-26-deploy-int-004-proof.md`

### 3. Analytics (INT-009)

```bash
# prod-smoke JWT branch
curl -sS -H "Authorization: Bearer $TOKEN" \
  "http://127.0.0.1:8000/api/v1/analytics/snapshot?period=7d" | head -c 200
```

Handoff: `docs/handoffs/2026-06-26-deploy-int-009-proof.md` · persist S3-01

### 4. Content calendar (INT-010)

Handoff: `docs/handoffs/2026-06-27-ga4-verify-phase-b2-e2e.md` · P2-03 PASS

### 5. Widget chat (INT-001)

- Route: `POST /api/v1/widget/chat` (no JWT; CORS whitelist)
- Code: `agent/customer_agent.py`

### 6. WP SSH agent

```bash
curl -sS http://127.0.0.1:8000/worker/health | grep ssh_connection
# → "ok"
```

Telegram: `/zadanie` → diff → HITL Tak/Nie → write or `/cofnij`

### 7. Worker + HITL

```bash
cd /opt/jadzia
./venv/bin/python3 scripts/send_task.py "/* jadzia-spine-proof */" --test_mode --dry_run
```

Dashboard (JWT): `GET /worker/dashboard`

### 8. Weekly brief

```bash
grep WEEKLY_BRIEF /opt/jadzia/.env
# Optional manual trigger on VPS:
cd /opt/jadzia && ./venv/bin/python3 -c "from agent.nodes.brief_node import send_weekly_brief; print(send_weekly_brief())"
```

---

## Auth baseline (post-remediation)

| Check | Expected |
|-------|----------|
| `JADZIA_ENV=production` | set |
| `POST /chat` without JWT | **401** |
| Worker routes without JWT | **401** |

Deploy closure: `docs/handoffs/2026-07-05-deploy-closure-complete.md`

---

## Open (not spine blockers)

| Item | Owner |
|------|-------|
| S1-01 secret rotation | Dowódca |
| VPS git vs SCP drift (behind `main` with INSPIRE) | Dowódca deploy hygiene |
| Commander playbook exercises | Dowódca |
| Procurement Phase C | Future |

---

## Re-run

```bash
ssh root@185.243.54.115 "bash /opt/jadzia/deployment/prod-smoke.sh"
```
