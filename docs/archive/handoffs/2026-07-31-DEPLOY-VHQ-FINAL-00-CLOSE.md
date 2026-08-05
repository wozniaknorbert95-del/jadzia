---
status: "[DEPLOY CLOSE]"
gate: "VF-VHQ-FINAL-00"
prod_tip: "53a19e2+"
runtime_tip: "see tip sync"
cache: "vhq-w67a"
backup: "/opt/jadzia/data/jadzia-pre-final-00-20260731.db"
founder_go: "Twój ruch · commit + deploy kompleksowo (2026-07-31)"
verdict: "DEPLOY PASS · dashboard_seal FINISHED_PARTIAL_LOOP"
---

# DEPLOY CLOSE — VF-VHQ-FINAL-00

## Deploy

1. Backup SQLite → `jadzia-pre-final-00-20260731.db` (~9.5 MB)
2. `git reset --hard origin/master` → tip includes FINAL UI `vhq-w67a`
3. `systemctl restart jadzia` → **active** · `/health` **ok**
4. Assets: Firm Chain only · no `#vhq-floors` · stage bands · Finish Card · deliver honesty

## Prod dogfood (`?v=vhq-w67a`)

Evidence: `docs/handoffs/evidence-vhq-final-prod/DOGFOOD.md`

| F-check | Result |
|---------|--------|
| F7 one nav axis | **PASS** |
| F2 Esc stay HQ | **PASS** |
| F3 Finish Card / Order unlock | **PASS** |
| F4 Deliver EV-W2-010 | **PASS** |
| F5 no fake S7 | **PASS** |
| F1 MC surfaces present | **PASS** (JWT empty honest) |

## Expert verdict (raw)

See section in tip-sync commit / operator response. Seal = **Director Dashboard FINISHED (partial_loop)** — not full factory.

## Rollback

```bash
cd /opt/jadzia && git checkout adafd83 && systemctl restart jadzia
# DB: jadzia-pre-final-00-20260731.db if needed
```

## Next

COM-AI resume (parked) · Order Desk SoT osobny · Ads freeze do 2026-08-06
