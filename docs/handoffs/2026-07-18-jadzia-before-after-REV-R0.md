# Jadzia — PRZED vs TERAZ (REV-R0 + COI spine)

**Date:** 2026-07-18  
**Purpose:** honest capability snapshot for Dowódca after Revenue Truth closeout (Gate D deferred)  
**Status:** REFERENCE  
**Related:** `2026-07-18-rev-r0-VERIFY-CLOSE.md`

## One-line

Jadzia went from **WP/Telegram code agent + basic order ingest** to a **COI ops spine with revenue truth (test vs real) proven in Mollie TEST** — missing only one authorized **LIVE** paid-order proof (Gate D), parked for budget.

---

## PRZED modernizacją (early COI / pre–Revenue War Room)

Rough baseline: Phase A v1 deploy era (INT-002 v1 ~2026-06) + classic agent.

| Area | What she could do |
|------|-------------------|
| WP edits | Telegram → queue → SSH read/write/rollback + HITL |
| Sales chat | Wizard widget (`INT-001`) |
| Orders | INT-002 **v1** webhook → `orders` row (status/total basics) |
| Leads | INT-004 ingest (after DEPLOY-02) |
| Analytics | INT-009 snapshot (GA4 read) — limited revenue hygiene |
| Content | Calendar + early FB text publish |
| Revenue truth | **No** durable test/real classification, **no** reconcile CLI, **no** v2 payment/attribution evidence |
| Cash path hygiene | COD still possible on store; no controlled Gate C/D program |

**She was:** a strong WP ops + chat backend with thin order plumbing.

---

## TERAZ (2026-07-18 — after REV-R0 + spine)

### Revenue Truth (this program)

| Capability | Status |
|------------|--------|
| INT-002 **v2** consumer (payment/test/attribution fields) | LIVE `@504fdf6` |
| zzpackage producer theme | LIVE `@bfe8485` |
| Classification (`real` / `test` / `unknown`) | LIVE + SQLite evidence |
| `revenue_reconcile.py` dry-run | LIVE (read-only; history preserved) |
| Contract + runbooks | In repo (`REVENUE-EVENT-CONTRACT-v1`, INT-002-V2-DEPLOY, REVENUE-RECONCILIATION) |
| Gate C — Mollie TEST paid `#3209` | **PASS** — `classification=test`, GA4 purchase gated off, `kpi_paid_eligible=false` |
| COD OFF + checkout iDEAL-only | **PASS** |
| Gate D — one LIVE real paid ≥199 | **DEFERRED** (no budget; min 199 unchanged) |
| jadzia PR #3 | **MERGED** → `master` |

### Parallel COI spine (same period, not only R0)

| Capability | Status |
|------------|--------|
| COI Commander UI + queue | LIVE |
| Marketing intake (GDrive) | LIVE |
| FB text / photo / video publish | LIVE (video E2E PASS) |
| SMTP Delegat escalation | LIVE |
| Design Agent INSPIRE | LIVE (enterprise merge) |
| Management CLI | LIVE |

**She is now:** ops COI + **revenue measurement hygiene** with a proven test-path exclusion from KPI. Real-money KPI proof waits on Gate D.

---

## Side-by-side

| Question | PRZED | TERAZ |
|----------|-------|-------|
| Can she take WC orders into SQLite? | Yes (v1) | Yes (v1+**v2**) |
| Can she tell test money from real KPI? | No | **Yes** (Gate C proven) |
| Can she reconcile without rewriting history? | No | **Yes** (dry-run CLI) |
| Is COD polluting checkout? | Often yes | **COD OFF**, iDEAL-only |
| Is LIVE paid revenue proven end-to-end? | No | **Not yet** (Gate D parked) |
| Marketing / FB / Commander? | Partial / early | **LIVE** text+photo+video + Commander |

---

## What she still cannot / should not do yet

- Gate D LIVE paid proof (budget)
- Auto strategy spawn from weekly brief (still ~40% synthesis)
- TikTok publish (pending / deferred)
- Secret history purge (S1-01 BFG — human)
- Blind `--apply-classifications` on prod without Dowódca review

---

## Honest % (same as prior briefing)

- **REV-R0 program:** ~85–90% (Gate D hole)
- **Operational spine (`brain.md`):** ~87–90%
- **Gate D alone:** 0% of that one criterion (deferred on purpose)

```text
BEFORE: WP agent + v1 orders + thin analytics
AFTER:  COI spine + v2 revenue truth + Gate C PASS; Gate D parked
NEXT:   budget + Mollie LIVE + GO Gate D — or leave parked
```
