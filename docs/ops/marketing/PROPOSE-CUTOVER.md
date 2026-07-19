---
status: "[ACTIVE]"
title: "Propose cutover — ADHD runbook (#2)"
updated: "2026-07-19 (LIVE tip 4ad1e99)"
---

# Propose cutover — jedna ścieżka

**Nie zastępuje** [MKT-BRAIN-PRO.md](./MKT-BRAIN-PRO.md).  
**Status LIVE:** `MB_MODE=propose` tip **`4ad1e99`** (GO 2026-07-19). Meta zostaje **#1**.

**Hard STOP:** Ads API create / Mollie. Re-flip tylko z nowym GO.

## Agent

```bash
cd /opt/jadzia
source venv/bin/activate
python scripts/mb_propose_preflight.py
python scripts/mb_propose_preflight.py --ticket
# lub API (po deploy tip z PREFLIGHT):
curl -sS -H "Authorization: Bearer $TOKEN" \
  http://127.0.0.1:8000/api/v1/commander/marketing/propose-preflight
```

| Verdikt | Znaczenie |
|---------|-----------|
| `READY_FOR_GO` | Evidence OK — czekamy na ticket GO |
| `BLOCKED` | Napraw checks; nie proś o flip |

## Dowódca (HITL)

1. Odbierz linię `go_ticket` (Telegram / agent).
2. Decyzja: **GO** albo **NIE**.
3. Po GO + deploy tip PREFLIGHT na VPS:
   `CONFIRM=GO_PROPOSE bash deployment/mkt-propose-cutover-vps.sh`
   (albo ręczny flip `MB_MODE=propose` + restart) — checklist §F4 w MKT-BRAIN-PRO.
4. Verify: brak `CB_SHADOW` · karty propose w TG · **Act nadal gated** tokenem.

## Ticket template

```
GO propose YYYY-MM-DD — accuracy=…% n=… — tip=… — preflight=READY_FOR_GO
```
