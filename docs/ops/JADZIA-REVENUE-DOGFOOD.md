# Jadzia — Revenue Dogfood (no payment)

**Purpose:** smoke Demand Engine 01→03 without Mollie / live charge.  
**Prerequisite:** VPS `/opt/jadzia` on `master` tip ≥ Demand-03 (FEATURE `367549f`, tip docs may be newer).  
**Canonical host:** `https://api.zzpackage.flexgrafik.nl` (prod nginx → jadzia `:8000`). Local/SSH: `http://127.0.0.1:8000`.  
**STOP:** no checkout pay, no Gate D, no plugin updates, no `_recover_*.py`.

**Related:** `docs/handoffs/2026-07-18-rev-demand-03-CLOSE.md` · Plan1 CLOSE `docs/handoffs/2026-07-18-ssot-demand-CLOSE.md`

---

## 1) Health (1 min)

```bash
curl -sS http://127.0.0.1:8000/worker/health | python3 -m json.tool | head -30
```

- Expect: `worker_loop_alive=true`, `sqlite_connection=true`
- `ssh_connection=error` + overall `degraded` = **known** (not a Demand fail)

## 2) Widget CTA — REV-DEMAND-01 / 02a (2 min)

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/widget/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"dogfood-demand-cta","message":"Ik wil een offerte voor mijn bestelbus"}'
```

- Expect: `reply` + `wizard_deeplink` non-null + `cta_sku` (AI mid/high or scorer; 02a max/intent gate)

## 3) Widget session durability — REV-DEMAND-02 (3 min)

```bash
SID=dogfood-demand-dur
curl -sS -X POST http://127.0.0.1:8000/api/v1/widget/chat \
  -H 'Content-Type: application/json' \
  -d "{\"session_id\":\"$SID\",\"message\":\"Durability marker ALPHA dogfood\"}" >/dev/null
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  "SELECT session_id, length(history_json) FROM widget_chat_sessions WHERE session_id='$SID';"
# Optional hard proof: systemctl restart jadzia; second turn same SID must retain ALPHA in history_json
```

- Expect: row in `widget_chat_sessions` for `$SID`

## 4) Widget lead — REV-DEMAND-01b (2 min)

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/widget/chat \
  -H 'Content-Type: application/json' \
  -d '{"session_id":"dogfood-demand-lead","message":"Bel me op dogfood.lead@example.nl akkoord toestemming"}'
```

- Expect: `lead_id` when email+consent present

## 5) INSPIRE lead — REV-DEMAND-03 (2 min)

On VPS (as `jadzia`, venv):

```bash
cd /opt/jadzia && source venv/bin/activate && python3 - <<'PY'
from agent.inspire.chat_advisor import _maybe_persist_inspire_lead
from agent.db import db_get_lead_by_email
email = "dogfood.inspire@flexgrafik.test"
msg = f"Bel me op {email} akkoord toestemming"
lid = _maybe_persist_inspire_lead(session_id="dogfood-inspire", message=msg, field_updates=None, brief_partial=None)
lead = db_get_lead_by_email(email)
print("lead_id", lid, "source", lead and lead.get("source"))
assert lead and lead.get("source") == "inspire"
PY
```

- Expect: `source=inspire` and non-null `lead_id`

## 6) Commander hot lead disposition — HUMAN (3 min)

1. Open `https://api.zzpackage.flexgrafik.nl/commander/` (JWT).
2. Analytics / Home: lead disposition Ack / Close / Snooze.
3. Closed/snoozed leaves hot queue.

API alternative:

```bash
curl -sS -X POST http://127.0.0.1:8000/api/v1/commander/leads/LEAD_ID/disposition \
  -H "Authorization: Bearer $JWT" -H 'Content-Type: application/json' \
  -d '{"disposition":"acked"}'
```

## 7) Cleanup

- Use `deployment/cleanup-e2e-hot-leads.py` for e2e/dogfood emails only.
- Do not delete real customer leads.

---

## 7) Brief → sales CTA tickets — REV-DEMAND-04 (2 min)

1. Ensure an open lead with `game_score >= 40` and disposition `open`/`acked`.
2. Trigger weekly brief spawn (worker interval or call `spawn_brief_sales_cta_tickets()` in a maintenance shell).
3. Commander Home queue: card `queue_type=sales_cta`, title `[Sales CTA] Follow up lead #…`.
4. Ack / Snooze / Close via disposition buttons (JWT `queue:act`).

## Pass criteria

- [ ] 1 Health: worker + sqlite OK (`ssh_connection=error` allowed)
- [ ] 2 Widget returns structured Wizard CTA (no pay)
- [ ] 3 Widget session durability row / restart proof
- [ ] 4 Widget lead with consent gets `lead_id`
- [ ] 5 INSPIRE lead `source=inspire`
- [ ] 6 Commander disposition (HUMAN JWT UI) — `ready_for_human` if skipped
- [ ] 7 Brief sales CTA ticket in Commander queue (`sales_cta`)
- [ ] 8 Zero Mollie charges

## Parks (unchanged)

Gate D / S1 / OPS-FB / B3 / TikTok remain in `todo.json`.
