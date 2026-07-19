# Handoff PROOF: COI Commander v3 — CLOSURE (2026-07-09)

**Program:** COI Commander v3 Closure (Sprints S0–S7)  
**Branch:** `feat/design-agent-inspire-v2`  
**Commit:** `a0182e3`  
**VPS:** `185.243.54.115` `/opt/jadzia` @ `a0182e3` — service **active**  
**Public URL:** https://api.zzpackage.flexgrafik.nl/commander/  
**Plan:** [`COI-COMMANDER-PLAN-v3.md`](../design/coi-commander/COI-COMMANDER-PLAN-v3.md) — **APPROVED**

---

## Sprint completion

| Sprint | Deliverable | Status |
|--------|-------------|--------|
| S0 | Plan APPROVED + workshop handoff | Done |
| S1 | N13 worker publish lock, calendar scope gate, authz matrix tests | Done |
| S2 | N6 escalation email/TG delegat, N16 health monitor | Done |
| S3 | ApprovalCard, 60s undo, deeplink ticket, WCAG nav, bulk UI, N4b | Done |
| S4 | Queue types, CE-10 freshness, N2 audit verify | Done |
| S5 | HOTL path, confidence_avg, revert spike | Done |
| S6 | commander_roles map, JWT --role, Settings UI | Done |
| S7 | Scorecard + closure handoff | Done |

---

## Scorecard 6/6

| Wymiar | Proof |
|--------|-------|
| Autorytet | `test_commander_authz_matrix.py` — delegat/viewer 403 |
| Odwracalność | unpublish API + `undo.py` 60s internal + UI bar |
| Wykrywalność | `escalation.py` 2nd recipient + `health_monitor.py` |
| Obciążenie | Home ≤7 chunks, PL UI, ApprovalCard |
| Ciągłość | `commander_roles` + `delegat_telegram_chat_id` settings |
| Rozliczalność | `verify_audit_chain()` + retention job |

---

## Test suite

```bash
pytest tests/unit/test_commander_*.py tests/unit/test_content_calendar_api.py tests/unit/test_auth_hardening.py -q
→ 42 passed (2026-07-09)
```

---

## Deploy PROOF (2026-07-09)

| Krok | Status |
|------|--------|
| Commit `a0182e3` (bez INSPIRE engine) | ✅ |
| Push `origin/feat/design-agent-inspire-v2` | ✅ |
| VPS pull + `systemctl restart jadzia` | ✅ |
| `deployment/commander-prod-smoke.sh` | ✅ **10/10 PASS** |

Smoke: `/commander/` local+public 200, queue, agents, tickets, CRITICAL queue, settings delegat, graduation, audit-log, delegat 403 pause.

---

## Pozostałe kroki (Dowódca)

1. TG `/ticket test opis` → signed link na telefonie
2. Otwórz `/commander/` z JWT — queue + undo60 UI
3. Merge `feat/design-agent-inspire-v2` → `master` po approve

---

## Backlog post-closure

- F4 Paid ads — IA placeholder only (Agents Phase C cards)
- INSPIRE `agent/inspire/engine.py` — osobny commit
- Live workshop human sign-off items w `WORKSHOP-F0-CHECKLIST.md`
