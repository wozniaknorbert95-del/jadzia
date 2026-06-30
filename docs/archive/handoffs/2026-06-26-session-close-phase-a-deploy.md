# Handoff — COI Phase A deploy complete + Phase B next

**Date:** 2026-06-26  
**Branch:** `master` @ `901ebcc`  
**Plan:** `docs/plans/PLAN-COI-PHASE-B.md`

---

## DONE (ta sesja + poprzednia kontynuacja)

### Deploy gates — CLOSED

| Gate | Proof |
|------|-------|
| **DEPLOY-01** INT-002 | WC order `3149` → jadzia `orders`; webhook OK (`wp_cli_synthetic`, Mollie test_mode=OFF) |
| **DEPLOY-02** INT-004 | PR#119 merged `917b630`; GHA deploy; leads E2E + duplicate |
| **DEPLOY-03** INT-009 | GA4 SA on VPS; property IDs in `.env`; pipeline `sync_status: success` (proof) |

### Prod (jadzia VPS `185.243.54.115`)

- `prod-smoke.sh` → **pass=7 fail=0**
- Tables: `orders` (SMOKE-1 + 3149), `leads` (INT-004 rows), `content_calendar`
- GA4: `/root/jadzia/secrets/ga4-service-account.json`, `GA4_PROPERTY_ID_APP=528764186`, `GA4_PROPERTY_ID_ZZPACKAGE=528785553`

### Git pushed

| Repo | Head | Note |
|------|------|------|
| jadzia-core | `901ebcc` | gates close, handoffs, `deploy01-wc-order-smoke.sh` |
| flexgrafik-meta | `eb41219` | INT-002, INT-004, INT-009 → **LIVE** |
| app.flexgrafik.nl | `6189c2b` on `main` | INT-004 deploy + smoke script |

### Meta contracts LIVE

INT-002, INT-004, INT-009 (INT-004/002/009 w `integration-contracts.md`)

---

## LEFT (następna sesja — agent plan + execution)

### 1. GA4 zzpackage Viewer — verify (~5 min)

Dowódca nadał SA **Viewer** na property `528785553`. Agent ma:

1. `systemctl restart jadzia` (cache TTL)
2. `GET /api/v1/analytics/snapshot?period=7d` → oczekiwane: `sync_status: success`, `sources.zzpackage` ≠ null, `errors: []`
3. Uzupełnić `docs/handoffs/2026-06-26-deploy-int-009-proof.md` jeśli PASS

### 2. Phase B.2 — plan + pierwszy E2E workflow (~1 sesja)

Kanoniczny plan do napisania/aktualizacji, potem implementacja:

```text
orders (3149) → GET /content-calendar/suggestions/orders
→ POST draft → PATCH pending_approval → Telegram alert
```

Out of scope tej sesji: FB/TikTok publish API (Phase B.2 duży krok później).

### 3. Opcjonalnie (backlog)

- Mollie UI test (prawdziwy checkout) — revenue video proof
- app.flexgrafik.nl: 4 flaky E2E na CI (nie blokuje prod)
- OPS-01: VPS user `jadzia` zamiast root

---

## RISKS

| Risk | Mitigacja |
|------|-----------|
| GA4 zzpackage nadal `PermissionDenied` | Sprawdzić SA email + property `528785553`; propagation ~kilka min |
| DEPLOY-01 bez Mollie UI | Order 3149 synthetic — OK dla gate; Mollie UI = optional |
| Uncommitted `coi-docs-alignment.md` | Osobny commit docs lub stash |
| `todo.json` `next_human` nieaktualne | Zaktualizowane w tym handoff |

---

## V-FILES

```
C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\todo.json
C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\plans\PLAN-COI-PHASE-B.md
C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\handoffs\2026-06-26-deploy-int-009-proof.md
C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\agent\nodes\content_calendar_node.py
```

---

## Scripts / proof paths

- `deployment/deploy01-wc-order-smoke.sh` — INT-002 repeat smoke (zzpackage SSH)
- `app.flexgrafik.nl/scripts/int004-e2e-smoke.sh` — INT-004 repeat smoke
- `deployment/prod-smoke.sh` — full VPS gate (on server)

---

## Uncommitted (jadzia-core)

- `docs/handoffs/2026-06-26-coi-docs-alignment.md` (modified, not in `901ebcc`)
