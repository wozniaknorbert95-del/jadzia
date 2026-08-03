---
status: "[PASS · LOCAL · HISTORICAL GATE]"
title: "DEMAND-OS-TOOL-PASS checklist"
updated: "2026-08-03"
gate: "DEMAND-OS-TOOL-PASS"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md"
superseded_by: "docs/handoffs/2026-08-03-DEMAND-OS-TOOL-INTEGRITY-SEAL-CLOSE.md"
---

# DEMAND-OS-TOOL-PASS

| # | Check | Evidence |
|---|-------|----------|
| 1 | A0 tip hygiene | PROGRAM-LANES B/B2 PARKED_LAST · GO-DAY TOOL FIRST · demand-os-execute TOOL FIRST |
| 2 | A1 starts ingest | `starts_ingest.py` · `hub ingest` · money-check starts_utm≥1 from fixture |
| 3 | A2 publish gate | `publish_gate_bridge.py` · DENY/ALLOW dry-run tests |
| 4 | A3 calendar SoT | [`CALENDAR-SOT.md`](./CALENDAR-SOT.md) · growth=JSON |
| 5 | A4 MCP facades | `ga4_adapter` · `gdrive_cf` · `widget_leads` · `tools/demand_os_mcp.py` |
| 6 | A5 TT transport stub | `LiveTikTokTransport` · comment PARKED |
| 7 | A6 A2A auto | Val PASS → publish_request ack · engage → engage_event |
| 8 | pytest demand_os | historical gate; current suite lives in seal close |
| 9 | Marketing | historical; current = TOOL FIRST · live P0 PARKED |
| 10 | F5 / VPS | parked_cash · STOP |

**Phase B (dashboard tip):** DONE local (`DOS-DASH-01..03`).  
**Next:** `MASTER-TODO-4.md` → **`4-TOOL-01`** (TOOL FIRST). Live P0 PARKED. Rule: `.cursor/rules/demand-os-tool-first.mdc`.
