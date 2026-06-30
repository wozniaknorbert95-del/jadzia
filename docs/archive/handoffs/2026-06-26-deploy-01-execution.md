# DEPLOY-01 — wykonanie (Dowódca)

**Gate:** DEPLOY-01  
**SOT:** [PLAN-DEPLOY-INT-002.md](../plans/PLAN-DEPLOY-INT-002.md)  
**Status:** AWAITING EXECUTION

Agent przygotował plan i kod. **Ty wykonujesz** (Zasada 11).

## Szybka kolejność

1. `openssl rand -hex 32` → secret na obie strony
2. `./deployment/deploy-to-vps.sh` + `WC_WEBHOOK_SECRET` w VPS `.env`
3. Smoke curl (Faza 3 w planie) → `SMOKE-1` w `orders`
4. Deploy theme zzpackage + `wp-config` constants
5. Mollie test order → realny `order_id` w `orders`
6. Wypełnij [2026-06-26-deploy-int-002-proof.md](./2026-06-26-deploy-int-002-proof.md)
7. `todo.json`: DEPLOY-01 → `completed`, odblokuj P1-02

## Po zamknięciu gate

- INT-002 → LIVE w `flexgrafik-meta/integration-contracts.md`
- Następny agent task: **P1-02** analytics (lub DEPLOY-02 po integracji app)

---
RECOMMENDED_NEXT: Faza 1 PLAN-DEPLOY-INT-002
