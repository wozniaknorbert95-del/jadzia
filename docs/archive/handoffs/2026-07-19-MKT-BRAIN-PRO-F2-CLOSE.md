---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO F2 — Governance + Breakers CLOSE"
gate: "MKT-BRAIN-PRO-F2"
updated: "2026-07-19"
result: "PASS (core) — Chroma RAG deferred F2b"
---

# MKT-BRAIN-PRO F2 — CLOSE (core)

## Done

| Item | Status |
|------|--------|
| `circuit_breakers.py` CB_SHADOW/MARGIN/PIXEL/DATA_STALE/SPEND/CPA | DONE |
| `governance.py` approval_token TTL 15m + execute | DONE |
| `POST /api/v1/marketing/actions/execute` | DONE |
| Telegram APPROVE → mint token (shadow still blocks execute) | DONE |
| Tables `marketing_approval_tokens`, `circuit_breaker_events` | DONE |
| pytest `test_mb_f2_governance.py` | DONE |

## Deferred (not fake PASS)

| Item | Why |
|------|-----|
| ChromaDB campaign RAG | Secondary; SQL shadow history covers degraded path |
| Ads API create on execute | PARK (hard STOP) — ticket/paste-ready only |
| `MB_MODE=propose` | Requires Dowódca 14d shadow review ≥70% |

## Human-only

| Item |
|------|
| Meta Events Manager Purchase/IC verify |
| 14d shadow accuracy review → GO for propose |
