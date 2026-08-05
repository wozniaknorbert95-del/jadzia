---
status: "[DEPLOY CLOSE]"
gate: "VF-VHQ-FIRM-IA-00"
prod_tip: "adafd83"
runtime_tip: "adafd83"
cache: "vhq-w66a"
backup: "/opt/jadzia/data/jadzia-pre-firm-ia-20260731.db"
founder_go: "GO DEPLOY VF-VHQ-FIRM-IA-00 (session 2026-07-31)"
verdict: "DEPLOY PASS"
---

# DEPLOY CLOSE — VF-VHQ-FIRM-IA-00

## Deploy

1. `git fetch` + `reset --hard origin/master` → **`adafd83`**
2. Backup SQLite → `jadzia-pre-firm-ia-20260731.db` (~9.5 MB)
3. `systemctl restart jadzia` → **active**
4. `/health` → `status=ok`
5. Assets: `vhq-w66a` in `index.html` + `sw.js`; Esc comment + Firm Chain + Tools CTA present

## Prod dogfood (`?v=vhq-w66a`)

| Check | Result |
|-------|--------|
| Cold open HQ / eyebrow Virtual HQ · FlexGrafik | PASS |
| Tools / Sign in (not Operations Console) | PASS |
| Firm Chain 1–4 visible | PASS |
| Floor tabs P3 Sterowanie … P0 Realizacja | PASS |
| Order Desk PARKED EV-W2-010 + firmRole + unlockHint | PASS |
| Money/risk + NBA still on MC | PASS |
| Esc Order Desk → MC (stays HQ) | PASS |

Prod URL: https://api.zzpackage.flexgrafik.nl/commander/?v=vhq-w66a&vhq=mc

## Rollback

```bash
cd /opt/jadzia && git checkout 0264f5d && systemctl restart jadzia
# restore DB only if needed: from jadzia-pre-firm-ia-20260731.db
```

## Next

`active_gate` → null · idle · optional Growth / COM-AI after Founder GO
