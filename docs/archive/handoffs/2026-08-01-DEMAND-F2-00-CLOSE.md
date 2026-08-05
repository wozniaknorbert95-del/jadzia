---
status: "[CLOSE · LOCAL]"
title: "DEMAND-F2-00 — Validator + content_calendar"
updated: "2026-08-01"
gate: "DEMAND-OS-F2-00"
deploy_vps: false
---

# CLOSE — DEMAND-F2-00 (local)

## Analiza → decyzja

Nie budujemy atrapy „MCP server”. Budujemy **deterministyczny gate** (reguły C.5) + **content_calendar** + CLI o nazwach narzędzi OS §E — to jest profesjonalny Day-1 MCP *tool surface*. HTTP MCP adapter = późniejszy cienki wrapper.

## Evidence

| Check | Result |
|-------|--------|
| pytest F1+F2 | **19 passed** |
| `audit-sample` | **10/10 PASS** |
| `f2 gate` bez tokena | **GATE DENY** |
| `f2 validate` clean caption | **PASS** + `pass_token` |
| Ads freeze | `2026-08-06` w silniku |

## Shipped

- `agent/demand_os/publish_request.py`
- `agent/demand_os/validator.py` (R1–R8)
- `agent/demand_os/content_calendar.py`
- `tools/demand_os_f2.py`
- `CONTENT-CALENDAR.json`
- `tests/test_demand_os_f2_validator.py`

## F1 polish (pre-GO)

- `UTM-AUDIT-SAMPLE.csv` + `audit-sample`
- VALIDATOR-LOG VOID for deleted bridge post

## Next

`GO BUILD demand-f3` — TT/FB connectors (read/comment allowlist).  
Organic publish tylko przez gate po świadomym HITL.
