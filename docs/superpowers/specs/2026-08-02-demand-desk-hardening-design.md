---
status: "[ACTIVE · ETAP 5b SPEC]"
title: "Demand Desk Hardening — design spec"
updated: "2026-08-02"
gate: "DEMAND-OS-DESK-5B-00"
design: "docs/ops/demand-os/DEMAND-CONTROL-PANEL-DESIGN.md"
contract: "docs/ops/demand-os/DESK-CONTRACT.md"
audit: "docs/handoffs/2026-08-02-DEMAND-OS-DASHBOARD-00-CLOSE.md"
---

# Etap 5b — Biuro Popytu Dashboard Hardening

## Decyzja

**Marketing = OUT** until separate Founder GO. Close tool 100% UI honestly (Hard DoD 15/15 + §8 Dowódca prod).

## Hard DoD matrix (SoT: DASHBOARD-00-CLOSE)

| # | Item | Target evidence |
|---|------|-----------------|
| 1 | HTML A0–F | `test_desk_html_ids_present` |
| 2 | Render 1:1 API | `test_render_desk_golden.py` |
| 3 | FIXTURE/PARKED/n/a | MIXED golden + banner tests |
| 4 | HITL no publish | static grep |
| 5 | Hunt dry + SENT | API + Playwright |
| 6 | ICP + ledger RBAC | extended API viewer 403 |
| 7 | VHQ CTA | `test_vhq_firm_ia_contracts` |
| 8 | Deep link | Playwright |
| 9 | no go_ready hero | static |
| 10 | static tests + nav 5 | desk-dash03 all test files |
| 11 | doctor + pytest | hub doctor |
| 12 | Manual §8 Dowódca | prod + design checkboxes |
| 13 | DESK-UI-HANDOFF | updated |
| 14 | CLOSE handoff | DEMAND-DESK-5B-CLOSE.md |
| 15 | marketing PARKED | no next=marketing in SoT |

## Sessions

| ID | Deliverable |
|----|-------------|
| S0 | SoT sync + this spec + supersede false SEAL handoffs |
| S1 | sanitized set-now + env + deploy sync script |
| S2 | AB/CD layout + UI contract gaps + desk-dash03 |
| S3 | skeleton, retry, keyboard, RBAC, responsive |
| S4 | unit/API tests |
| S5 | Playwright E2E + phone checklist |
| S6 | cruft sweep docs + commander-ui |
| S7 | Dowódca §8 + CLOSE (deploy only GO) |

## IA — three entry points

| Surface | Role |
|---------|------|
| Biuro Popytu (nav / More) | **Primary** ops day |
| VHQ Marketing Studio | Hop → Biuro Popytu |
| Marketing tab | Legacy organic observe |

## Non-goals

GO MARKETING HITL · live publish · Ads · VPS without GO · fake SEAL

## Verify gate

```bash
python tools/demand_os_hub.py doctor
pytest tests/unit/test_demand_desk* tests/test_demand_desk* tests/test_demand_os_api_desk.py tests/test_demand_os_desk_contract.py -q
```
