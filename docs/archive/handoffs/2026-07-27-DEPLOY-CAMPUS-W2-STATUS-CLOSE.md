---
status: "[CLOSED]"
title: "DEPLOY Campus W2 status fixes — tip df3d59a LIVE"
updated: "2026-07-27"
gate: "DEPLOY-CAMPUS-W2-STATUS"
prod_tip: "df3d59a"
cache: "campus-w01"
commit: "df3d59a"
w3_started: false
---

# Handoff — 2026-07-27 — Deploy W2 status fixes

## Sequence

| Step | Result |
|------|--------|
| W2 CLOSE | DONE |
| commit W2 status fixes | **`df3d59a`** |
| GO deploy | Founder GO this session |
| Prod verify | **PASS** |
| GO VF-CAMPUS-W3 | **not started** — await HITL |

## Deploy evidence

| Check | Result |
|-------|--------|
| Push `origin/master` | `cc9aa0f..df3d59a` |
| VPS `/opt/jadzia` tip | **`df3d59a`** (`TIP_MATCH=OK`) |
| SQLite backup | `jadzia-pre-campus-w2-20260727-170410.db` |
| `systemctl is-active jadzia` | **active** |
| Local `/health` | OK (Strona OK) |
| `/worker/health` | **degraded** SSH (pre-existing · `INC-SSH-RECOVERY-00`) |
| Public `?v=campus-w01` | HTTP **200** · EV-W2-001/005/006/009 · auth OK · NOT a Production desk · no EV-002 · no pending W2 |

## Next (HITL)

```text
GO VF-CAMPUS-W3
```

Do not auto-start W3. Residuals from W2 CLOSE remain (OS/VCMS PARTIAL, Knowledge/Analytics UNVERIFIED, Compliance session, SSH DEGRADED).
