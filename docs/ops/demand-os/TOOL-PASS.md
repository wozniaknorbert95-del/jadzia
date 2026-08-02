---
status: "[PASS · LOCAL]"
title: "DEMAND-OS-TOOL-PASS checklist"
updated: "2026-08-01"
gate: "DEMAND-OS-TOOL-PASS"
os_target: "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md"
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
| 8 | pytest demand_os | **47 passed** |
| 9 | Marketing | **PARKED_LAST** · no live publish |
| 10 | F5 / VPS | parked_cash · STOP |

**Phase B (dashboard tip):** DONE local (`DOS-DASH-01..03`).  
**Next:** PROGRAM SEAL (`hub doctor`) · Founder only `GO MARKETING HITL` (PARKED_LAST until then).
