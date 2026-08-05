---
status: "[DEPLOY CLOSE · PASS]"
gate: "COM-AI-50-SHIP"
updated: "2026-07-31"
vps_tip: "fcf6a9f"
backup: "/opt/jadzia/data/jadzia-pre-com-ai-50-ship-20260731-143113.db"
founder_go: "GO DEPLOY COM-AI-50-SHIP (2026-07-31 session)"
verdict: "DEPLOY PASS · widget ai_disclosure LIVE"
---

# DEPLOY CLOSE — COM-AI-50-SHIP

## Deploy

1. Backup → `jadzia-pre-com-ai-50-ship-20260731-143113.db` (~9.3 MB)
2. `git pull` `957b13f` → **`fcf6a9f`**
3. `systemctl restart jadzia` → **active** · `/health` **ok**
4. Smoke `POST /api/v1/widget/chat` → `ai_disclosure_ok` · `reply_prefixed` · **SMOKE_PASS**

## Canonical NL (prod)

`Je chat met een AI-assistent van FlexGrafik. Wil je een mens? Laat het weten — we nemen over.`

## Rollback

```bash
cd /opt/jadzia && git checkout 957b13f && systemctl restart jadzia
```

## Next

- Counsel przed organic ≥2026-08-02  
- Evidence screenshot przy pierwszym publish  
- Ads freeze do 2026-08-06  
