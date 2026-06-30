# Handoff — DEPLOY-01 prod execution (2026-06-26)

**Stage:** L4-Closed (deploy infra)  
**Gate:** DEPLOY-01 **PARTIAL** — smoke OK, Mollie E2E pending

## Git (pushed)

| Repo | Commit | Branch |
|------|--------|--------|
| jadzia-core | `a22c3d6` (+ deploy proof follow-up) | master |
| zzpackage | `ae29e79` | main |
| flexgrafik-meta | `7994ac5` | main |

## Produkcja — wykonane

1. **jadzia VPS** — kod wgrany (tar), `pip install`, restart `jadzia`
2. **Sekrety** — `WC_WEBHOOK_SECRET` + `LEADS_API_KEY` w `/root/jadzia/.env`
3. **Schema** — tabele `orders`, `leads` na prod DB
4. **Smoke INT-002** — `SMOKE-1` → `db_status: success`, `order_internal_id: 1`
5. **zzpackage wp-config** — `FG_JADZIA_WEBHOOK_URL` + `FG_JADZIA_WEBHOOK_SECRET` (backup wp-config)
6. **zzpackage theme** — GHA [28231465724](https://github.com/wozniaknorbert95-del/zzpackage/actions/runs/28231465724) OK, `fg-jadzia-order-webhook.php` on server

## Zostało (Dowódca, ~15 min)

Mollie **test mode** — złóż zamówienie w Wizard → sprawdź:

```bash
sqlite3 /root/jadzia/data/jadzia.db \
  "SELECT order_id,status,total_gross FROM orders ORDER BY id DESC LIMIT 1;"
```

Po realnym WC `order_id`: zamknij `docs/handoffs/2026-06-26-deploy-int-002-proof.md`, INT-002 → LIVE w meta, `DEPLOY-01` → completed w todo.

## Sekrety

**Nie w repo.** Lokalizacja: jadzia `/root/jadzia/.env`, zzpackage `wp-config.php`.

---
RECOMMENDED_NEXT: Mollie test checkout
WHY_NEXT: Ostatni krok zamknięcia DEPLOY-01
