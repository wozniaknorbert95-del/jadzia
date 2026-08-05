---
gate: DEMAND-OS-DESK-5E-00
status: CLOSE · gap-close P1/P2 agent · Dowódca §8 pending
updated: 2026-08-02
parent: docs/handoffs/2026-08-02-DEMAND-DESK-5D-IA-CLOSE.md
spec: docs/superpowers/plans/2026-08-02-demand-desk-gap-close.md
---

# CLOSE — Etap 5e Biuro Popytu gap-close (agent)

## Werdykt

**P1/P2 z planu gap-close wdrożone.** Sesja przy boot stabilna · hierarchia Praca→Puls w DOM · prod data sync.

## Deliverables

| ID | Fix | Status |
|----|-----|--------|
| B1 | `bootstrapAuth` nie woła `refresh()` przed `vhqBoot` | ✅ |
| B1b | VHQ KPI enrich `authCritical: false` | ✅ |
| U24 | `#desk-praca` przed `#desk-puls` w HTML | ✅ |
| P4 | `.desk-queue-row:focus-visible` keyboard | ✅ |
| S1 | VPS sync sanitized set-now + `DEMAND_OS_SET_NOW` | ✅ deploy |
| Cache | desk-dash06 | ✅ |

## Verify

```bash
python -m pytest tests/unit/test_demand_desk_ui_contracts.py tests/e2e/test_demand_desk_flow.py tests/unit/test_commander_complete_ui.py tests/unit/test_render_desk_golden.py -q
```

Prod: `https://api.zzpackage.flexgrafik.nl/commander/?cb=desk-dash06`

## Dowódca — §8 (human)

Checklist: [`DESK-PHONE-SMOKE-CHECKLIST.md`](../ops/demand-os/DESK-PHONE-SMOKE-CHECKLIST.md)

Hard DoD #12 → **15/15 dopiero po §8 prod**.

Marketing **PARKED_LAST**.
