---
status: ACTIVE
updated: "2026-08-03"
target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md (v5 INSIDER)"
map: "docs/ops/SYSTEM-FIRM-OPERATING-MAP.md"
rule: "tool-only scope — marketing live PARKED until Dowódca unlock"
---

# OS TARGET v5 — pokrycie sekcji „Agenci” (stan vs cel)

Legenda: `done` (kod + testy) · `waiting` (tool gotowy, brak części) · `parked` (live/human — czeka na unlock)

## §E Agentic Architecture (hub-spoke)

| Element TARGET | Stan | Dowód / nota |
|----------------|------|--------------|
| Hub = Agent_Growth_Lead | `done` | rola `growth_lead` w registry (status/money_check/weekly/doctor/sync_starts) |
| Spokes: ICP, CF, TT, FB, Blog, Sales, CRE, Validator | `done` | 9 ról w `agent/demand_os/agents/registry.py` |
| Łańcuch ICP→CF→Val→Publish | `done` (tool) | `hub agents flow` — pełny chain: ICP→fatigue(B.4)→CF→Val→handoff→calendar bind (`--apply`), publish gated |
| TT/FB→Sales→CRE→Wizard | `done` (tool) | `sales list_hot/sync_hot` · `cre` hot leads → deeplink rule |
| A2A: brief_icp · publish_request · engage_event · lead_hot | `done` | `a2a_bus.py` 4 typy + SLA (0/5/15/15 min) |
| MCP: jadzia.db+UTM | `done` | UTM Lock + growth_events + attribution SQLite |
| MCP: content_calendar | `done` | `content_calendar.py` + F2 calendar/gate |
| MCP: GA4 | `waiting` | fail-closed stub `done`; live = brak credentials. Contract: plik SA (`GOOGLE_APPLICATION_CREDENTIALS` musi istnieć na dysku) **lub** inline `GA4_CREDENTIALS_JSON='{"type":"service_account",...}'` — path/garbage w inline nie włącza live (test) |
| MCP: publish path | `parked` | test-only publish→delete; live gated |
| MCP: GDrive | `waiting` | `list_cf_assets_stub` — real GDrive connector TO-BE |
| MCP: widget/leads | `done` | `widget_leads.py` hot leads + A2A sync |
| MCP: social connectors read/comment | `parked` | TARGET mówi TO-BE; `engage-dry` mock only |

## §H Insider job spec (role)

| Rola | Spec TARGET | Stan |
|------|-------------|------|
| Agent_TT | publish ≥3/tydz · auto reply · outbound | shell `done`; publish/reply/outbound `parked` |
| Agent_FB | allowlist read · comment 1+1 | shell `done`; live comment `parked` |
| Agent_Blog | 1 ICP/article · SEO ZZP | pipeline `done` (drafts); ship `parked` |
| Agent_Sales | STL · zero overnight | `done` (STL monitor + hot sync) |
| Agent_Sniper_Validator | gate przed światem | `done` (9 reguł C.5 + gate + pass_token) |
| Agent_Growth_Lead | Money Check · ICP week · kill vanity | `done` (money_check + weekly + doctor) |

## §J Rollout Waves — `hub agents wave-check`

| Wave | Tool | Live PASS |
|------|------|-----------|
| W1 Hub+ICP+TT+Sales+Validator | `tool_ready` | `parked` — 3 TT/tydz + ledger cadence (human) |
| W2 +CF +FB hunter | `tool_ready` | `parked` — comments daily |
| W3 +Blog ICP | `tool_ready` | `parked` — 1 article/tydz shipped |
| W4 full auto engage + episodic | `tool_ready` (episodic layer) | `parked` — starts WoW ↑ |

**Reguła:** `tool_ready ≠ live PASS`. Live PASS = human cadence po unlock — nigdy auto-zaliczane.

## Co CZEKA (kolejność, tool-only)

1. GA4 live — credentials (plik SA lub inline JSON) na VPS + `DEMAND_OS_GA4_LIVE=1` (GO).
2. GDrive real connector (zastąpić stub) — bez GO na network.
3. Desk tile „Demand OS Agenci” z `list_agents()` (w realizacji — MASTER-TODO-6 6-10).
4. Worker loop per rola → dopiero wtedy `shell: false`.

Postęp Etap 6: heartbeat per rola `done` · owner-verify gate `done` · coverage agents ≥80% `done` · flow calendar+fatigue `done` · W4 real checks `done` · GA4 inline contract `done`.

## Co jest POZA (marketing — PARKED do unlock)

- Live TT/FB/blog publish · auto reply · outbound engage
- Social connectors live · Ads (freeze do 2026-08-06 + unlock)
- Live PASS waves (cadence to praca Dowódcy/HITL, nie kodu)
