---
status: "[DEPLOY CLOSE · PASS]"
gate: "VF-ORDER-DESK-WV-00"
updated: "2026-07-31"
prod_url: "https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w68a"
vps_tip: "eb3c45e"
cache: "vhq-w68a"
backup: "/opt/jadzia/data/jadzia-pre-order-desk-wv-20260731-141246.db"
founder_go: "GO DEPLOY VF-ORDER-DESK-WV-00 (2026-07-31 session)"
verdict: "DEPLOY PASS · Order Desk mirror RO · EV-W2-010 still PARKED"
---

# DEPLOY CLOSE — VF-ORDER-DESK-WV-00

## Deploy

1. Backup SQLite → `jadzia-pre-order-desk-wv-20260731-141246.db` (~9.2 MB)
2. `git pull --ff-only` `76788d9` → **`eb3c45e`**
3. `systemctl restart jadzia` → **active** · `/health` **ok**
4. Assets: `vhq-w68a` · `#vhq-work-order-mirror` · SW cache `coi-commander-shell-vhq-w68a`

## Prod dogfood (`?v=vhq-w68a`)

| Check | Result |
|-------|--------|
| HTTP 200 | **PASS** |
| Mirror section present | **PASS** |
| `vhqRenderOrderDeskMirror` + SoT ACCEPTED | **PASS** |
| `order-desk` status PARKED · EV-W2-010 | **PASS** |
| No `#vhq-floors` / P3 Sterowanie | **PASS** |
| Unpark / S7 LIVE | **not claimed** (correct) |

## Rollback

```bash
cd /opt/jadzia && git checkout 76788d9 && systemctl restart jadzia
# DB if needed: jadzia-pre-order-desk-wv-20260731-141246.db
# UI cache: ?v=vhq-w67a
```

## Next

- Parallel HITL: COM-AI ACCEPT  
- EV-W2-010 unpark only after D5 U2–U8 + `GO UNPARK`  
- S7 remains `blocked_sot`
