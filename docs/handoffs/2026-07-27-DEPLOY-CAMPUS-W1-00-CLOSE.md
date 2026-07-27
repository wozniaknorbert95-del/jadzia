---
status: "[CLOSED]"
title: "DEPLOY-CAMPUS-W1-00 — campus-w01 LIVE on VPS"
updated: "2026-07-27"
gate: "DEPLOY-CAMPUS-W1-00"
prod_tip: "cc9aa0f"
cache: "campus-w01"
---

# Handoff — 2026-07-27 (DEPLOY-CAMPUS-W1-00)

## Sequence executed

| Step | Result |
|------|--------|
| W1 CLOSE | completed earlier |
| Commit W1 | **`cc9aa0f`** on `origin/master` |
| GO DEPLOY | Founder sequence + SSH pull |
| Prod verify | PASS (HTML markers) |
| W2 / W3 | **not started** — await Founder GO |

## Deploy evidence

| Check | Result |
|-------|--------|
| VPS `/opt/jadzia` tip | **`cc9aa0f`** |
| `systemctl is-active jadzia` | **active** |
| Local health on VPS | OK (Strona OK) |
| Public Commander `?v=campus-w01` | HTTP **200** · `campus-w01` · Mission Control · PARKED · NO ACTIVE CAMPAIGN · queue-list |
| `/worker/health` | **degraded** SSH (pre-existing) · worker+sqlite OK |

## Proposed next (HITL)

1. Founder dogfood: https://api.zzpackage.flexgrafik.nl/commander/?v=campus-w01  
2. **`GO VF-CAMPUS-W2`** — Trust hop contracts  
3. Then W3 truth cards  

**Do not** auto-start W2/W3/MKT.

## Git

- Commit: `cc9aa0f`  
- Push: origin/master  
- Unstaged residual: MKT parked materials (not this deploy)
