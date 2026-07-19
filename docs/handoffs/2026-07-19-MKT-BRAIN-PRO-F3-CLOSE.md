---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO F3 — Brain Bus CLOSE"
gate: "MKT-BRAIN-PRO-F3"
updated: "2026-07-19"
result: "PASS (local pytest 4/4) — VPS deploy pending commit+GO tip"
---

# MKT-BRAIN-PRO F3 — CLOSE

## Pre-check (session)

| Item | Status |
|------|--------|
| L0 `InitiateCheckout` Test Events | **PASS** 15:24:32 pixel `1084197063740065` |
| L0 `Purchase` | PARK (no Mollie GO) — does not block F3 |
| F0–F2 | completed / LIVE shadow |

## Done

| Item | Status |
|------|--------|
| `POST /api/v1/brain-bus/events` + `X-Brain-Bus-Secret` | DONE |
| Handlers: `system.health.degraded` / `recovered` / `ceo.priority` | DONE |
| Quality flag `vcms/ecosystem_red` + `CB_ECOSYSTEM` | DONE |
| Commander ticket + Telegram alert on degraded | DONE |
| CEO stub `POST …/brain-bus/ceo-priority` | DONE |
| Commander `GET …/brain-bus` analytics | DONE |
| pytest `tests/unit/test_mb_f3_brain_bus.py` | **4/4** |

## VCMS → jadzia (ops)

```bash
curl -sS -X POST "https://api.zzpackage.flexgrafik.nl/api/v1/brain-bus/events" \
  -H "Content-Type: application/json" \
  -H "X-Brain-Bus-Secret: $BRAIN_BUS_SECRET" \
  -d '{"event_type":"system.health.degraded","source_brain":"vcms","payload":{"conflicts":1,"summary":"conflicts.md > 0"},"correlation_id":"vcms-scan-YYYYMMDD"}'
```

Recovered: `event_type=system.health.recovered` with `conflicts:0`.

VPS: set `BRAIN_BUS_SECRET` in `/opt/jadzia/.env` (never commit).

## Human / next

| Item |
|------|
| Commit + deploy tip (Zasada 11) |
| Wire VCMS `vcms-scan` post-hook (flex-vcms) to webhook |
| 14d shadow review ≥70% before `MB_MODE=propose` |
| F2b Chroma optional; F4 Act only post-shadow GO |
