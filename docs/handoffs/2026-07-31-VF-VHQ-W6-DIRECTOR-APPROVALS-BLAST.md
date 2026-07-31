---
status: "[SUPERSEDED-BY-CLOSE]"
title: "VF-VHQ-W6-DIRECTOR-APPROVALS — BLAST (Approval Vault UX)"
updated: "2026-07-31"
gate: "VF-VHQ-W6-DIRECTOR-APPROVALS"
founder_go: true
founder_go_note: "GO W6 via Founder plan accept + Implement instruction 2026-07-31"
prod_baseline: "43a88d2 / vhq-w50a"
cache_target: "vhq-w60a"
commit: false
deploy: false
close: "docs/handoffs/2026-07-31-VF-VHQ-W6-DIRECTOR-APPROVALS-CLOSE.md"
---

# BLAST — VF-VHQ-W6-DIRECTOR-APPROVALS

**Surface (1-1-1):** Approval Vault Work View + L2 Approve/Reject on Ops Bus + L3/L4 STOP display + MC pending count  
**Backend:** reuse W5 `POST .../ops-bus/events/{id}/approval` (no new engine)  
**Cache:** `vhq-w60a`

## DoD (gate)

- D1 Vault Work View shell
- D2 Pending `approval_needed` list from API
- D3 L2 Approve/Reject + confirm + audit
- D4 L3/L4 STOP · no Approve button · API 403 preserved
- D5 Source-room teleport + MC real pending count
- D6 pytest + local dogfood evidence
- D7 CLOSE + COMMIT allowlist (no MKT)
- D8 Deploy only with separate GO (this session: implement mandate includes T8)

## STOP

No side effects on approve · no silent L3/L4 · no Ads/Mollie · no Order LIVE · no MKT

## Staging allowlist

```text
commander-ui/app.js
commander-ui/index.html
commander-ui/styles.css
commander-ui/sw.js
api/routes/ops_bus.py
tests/unit/test_ops_bus.py
todo.json
.cursor/current-task.md
docs/handoffs/2026-07-31-VF-VHQ-W6-DIRECTOR-APPROVALS-*.md
docs/handoffs/evidence-vhq-w60-dogfood/
```

BLAST_VERDICT: **CLOSED locally** — see CLOSE handoff · deploy under GO
