# Jadzia Spine Proof Matrix

**Date:** 2026-07-08  
**VPS:** 185.243.54.115 `/opt/jadzia` @ `463e5e0`  
**Runner:** `deployment/spine-proof-run.sh`

---

## Baseline (SC85-F2-01)

| Check | Result | Evidence |
|-------|--------|----------|
| Service `jadzia` | **PASS** | `active` |
| prod-smoke | **PASS** | `pass=8 fail=0`, orders count=31 |
| Git sync | **PASS** | local=`463e5e0`, origin=`463e5e0` |
| Auth `/chat` no JWT | **PASS** | HTTP **401** (body with `chat_id`) |

---

## Spine capabilities C1–C7

| ID | Capability | Result | Evidence (2026-07-08) |
|----|------------|--------|------------------------|
| C1 | Orders INT-002 | **PASS** | `order_id=3149` in `jadzia.db` |
| C2 | Leads INT-004 | **PASS** | `leads` count=5; DEPLOY-02 handoff |
| C3 | GA4 INT-009 | **PASS** | `sync_status=success`, period last_7_days |
| C4 | Calendar INT-010 | **PASS** | `entries` JSON, entry_id=3 |
| C5 | Widget INT-001 | **PASS** | NL `reply` re voertuigreclame pricing |
| C6 | WP SSH + Worker dry_run | **PASS** | task `cae68282` status=`completed`, dry_run=true |
| C7 | Weekly brief | **PASS** | `send_weekly_brief()` → `True` |

**C6 note:** First attempt (`0908f7c3`) status=error; retry with instruction „Pokaz status systemu bez zmian w plikach” → completed (SC85-F2-04).

---

## Supplementary checks

| ID | Check | Result | Evidence |
|----|-------|--------|----------|
| C8 | Portal INT-012 | **PASS** | `smoke-portal-qualify.ps1` ALL PASS |
| C9 | Dashboard JWT | **PASS** | `total_tasks` in `/worker/dashboard` JSON |

---

## Telegram manual (SC85-F2-03 / F4 E2)

| Step | Command | Status | Dowódca |
|------|---------|--------|---------|
| T1 | `/pomoc` | **MANUAL** | Wykonaj w bocie; potwierdź w F4 handoff |
| T2 | `/status` | **MANUAL** | Wykonaj po T1 |
| T3 | `/zadanie` + pytanie | **MANUAL** | E2: diff → odrzuć **Nie** |

---

## Summary

| Metric | Value |
|--------|-------|
| C1–C7 automated | **7/7 PASS** |
| Baseline | **4/4 PASS** |
| Telegram | **3 steps — Commander manual** (playbook F4) |

**Gate:** Spine 85% operational proof **CLOSED** for automated checks. S1-01 secret rotation remains open.
