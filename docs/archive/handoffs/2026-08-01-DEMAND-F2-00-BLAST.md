---
status: "[BLAST · CLOSED LOCAL]"
title: "DEMAND-F2-00 — Sniper Validator engine + content_calendar"
updated: "2026-08-01"
gate: "DEMAND-OS-F2-00"
todo: DOS-F2-01 · DOS-A2A-01 · DOS-MCP-01
founder_go: "GO BUILD demand-f2 (Dowódca 2026-08-01 after F1 verify)"
runtime_changes_allowed: false
deploy_vps: false
---

# BLAST — DEMAND-F2-00

## Potrzeba (dlaczego nie amatorsko)

HITL checklist w markdown **nie jest** systemem. Potrzebujemy:

1. **Deterministyczny Validator** — te same inputy → ta sama decyzja (rule IDs R1–R8 = C.5 1:1).
2. **`publish_request` A2A** — formalny obiekt; bez PASS **nie ma** prawa publikacji.
3. **PASS token** — dowód decyzji (asset + hash); ledger/validator-log powiązane.
4. **content_calendar** — strukturalny tydzień (TT/FB/Blog), nie luźny WEEK-CALENDAR.md.
5. **MCP = tool surface** — Python API + CLI z nazwami narzędzi OS §E; pełny MCP HTTP server = późniejszy slice (nie atrapa „JSON MCP” bez egzekucji).
6. **UTM Lock F1 = dependency** — Validator woła `validate_utm_url`, nie duplikuje regexów.
7. **Latency** — mierzona decyzja (&lt;5 min SLA; lokalnie ms).

## Anti-patterns (STOP)

| Amatorskie | Profesjonalne |
|------------|---------------|
| Markdown checkbox = „MCP” | Rule engine + log + token |
| Soft FAIL „ostrzeżenie” | Binary PASS/FAIL; FAIL = hard stop |
| 15 agentów / dashboard | 1 gate: publish_request → Val |
| Auto-publish w F2 | Gate only; publish HITL / F3 |
| Osobny UTM parser | Reuse `agent.demand_os.utm_lock` |

## Binary DoD

| # | DoD | Pass when |
|---|-----|-----------|
| D1 | `PublishRequest` schema | required fields + content_type |
| D2 | Validator R1–R8 | każdy rule ma golden FAIL test |
| D3 | PASS token | emitowany tylko przy PASS; log CSV |
| D4 | content_calendar | JSON week + list/add/set_status CLI |
| D5 | CLI gate | `validate` / `calendar` / `gate` |
| D6 | pytest | green; F1 tests still green |
| D7 | SLA field | `decision_ms` w wyniku |

## Work packages

1. **WP-A** `publish_request.py` · `validator.py`
2. **WP-B** `content_calendar.py` + `CONTENT-CALENDAR.json`
3. **WP-C** `tools/demand_os_f2.py`
4. **WP-D** tests + SoT tip

## STOP

TT publish · Ads · VPS · fake MCP server · Wave2 agents · HQ polish
