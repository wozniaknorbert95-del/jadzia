# Jadzia — Revenue Dogfood (15 min, no payment)

**Purpose:** smoke the Demand Engine agents without Mollie / live charge.  
**Prerequisite:** VPS `/opt/jadzia` on `master` containing REV-DEMAND-01b/c (widget CTA + lead disposition).  
**STOP:** no checkout pay, no Gate D, no plugin updates.

## 1) INSPIRE (3 min)

```bash
# On VPS or via HTTPS design-agent health / generate smoke
curl -sS https://YOUR_JADZIA_HOST/api/v1/design-agent/health
```

- Expect healthy / known smoke route.
- Optional: one generate → copy `wizard_deeplink` (do **not** pay).

## 2) Widget chat (5 min)

```bash
curl -sS -X POST https://YOUR_JADZIA_HOST/api/v1/widget/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"dogfood-demand-1","message":"Ik wil een offerte voor mijn bestelbus"}'
```

- Expect JSON with `reply` and, for mid/high intent, `wizard_deeplink` + `cta_sku`.
- Optional second message with email + consent:

```json
{"session_id":"dogfood-demand-1","message":"Bel me op dogfood.lead@example.nl akkoord toestemming"}
```

- Expect `lead_id` when email+consent present.

## 3) Commander hot lead (5 min)

1. Open Commander UI (JWT).
2. Home queue: hot_lead for high score (≥80) if present.
3. Click **Ack** / **Close** / **Snooze**.
4. Closed/snoozed leaves hot queue.

API:

```bash
curl -sS -X POST https://YOUR_JADZIA_HOST/api/v1/commander/leads/LEAD_ID/disposition \
  -H "Authorization: Bearer $JWT" -H 'Content-Type: application/json' \
  -d '{"disposition":"acked"}'
```

## 4) Cleanup

- Use `deployment/cleanup-e2e-hot-leads.py` for e2e emails only.
- Do not delete real customer leads.

## Pass criteria

- [ ] Widget returns structured Wizard CTA (no pay)
- [ ] Lead with consent gets `lead_id`
- [ ] Commander can disposition hot_lead
- [ ] Zero Mollie charges

## Related

- Program handoff: `docs/handoffs/2026-07-18-rev-demand-01-CLOSE.md`
- Parks: Gate D / S1 / OPS-FB / B3 / TikTok remain in `todo.json`
