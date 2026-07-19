---
status: "[ACTIVE]"
title: "MKT-BRAIN-PRO — plan Final Polish + F0 ready"
gate: "MKT-BRAIN-PRO"
updated: "2026-07-19"
result: "PLAN_COMPLETE — F0 ready_for_agent"
---

# MKT-BRAIN-PRO — handoff sesji planowania

## Git (sesja zamykająca)

| Pole | Wartość |
|------|---------|
| Branch | `master` |
| Tip | `b8c74df` — docs(marketing): META-PACK-01 lean READY |
| Uncommitted | `MKT-BRAIN-PRO.md` (new), `todo.json`, `README.md`, `session-state.md` |

**Commit nie wykonany** — Dowódca nie prosił. Przed VPS: commit + push planu.

## Co zrobiono (ta sesja)

| Deliverable | Evidence |
|-------------|----------|
| Audyt marketing automation | AUDIT-MKT-AUTO-01 — tylko FB organic LIVE w kodzie |
| Porównanie wizja vs AS-IS vs TO-BE | multi-brain, Agent OS vs jadzia, research OODA-G |
| Plan MKT-BRAIN-PRO v1 | post-audit: DTL, EDC, Shadow, Governance |
| **Final Polish** | Organic-to-Paid, Telegram-first HITL, Profit Watchdog, Hypothesis Ledger |
| Backlog tasks | `MKT-BRAIN-PRO-F0` ready · F1–F3 blocked |
| SoT | `docs/ops/marketing/MKT-BRAIN-PRO.md` |
| Pointers | `docs/ops/marketing/README.md`, `todo.json` |

## Co NIE zrobiono (uczciwie)

| Item | Status |
|------|--------|
| Kod F0 (DTL schema, ingest, UI) | **NOT STARTED** |
| META-PACK LIVE (L0 Events + €10 kampania) | **ready_for_human** — Dowódca |
| Deploy VPS | **NO GO** — standing_go_closeout=false |
| Commander dogfood | **PARK** — przerwany context-reset |

## Architektura — decyzje zamknięte

1. **Runtime MB** = jadzia VPS (nie Agent OS, nie PC)
2. **Build** = Cursor primary
3. **Agent OS** = Engineering Brain (kod 8 repo) — optional
4. **HITL primary** = Telegram inline approve (reuse `api/telegram.py` pattern)
5. **Commander** = Data Health / analytics only (secondary)
6. **North Star** = Net Margin per Acquisition + CPA_wizard (nie samo Meta CPA)
7. **F0** = Observability 2w na **prawdziwych** danych — nie fake prod sandbox
8. **F1** = Shadow 14d przed Act
9. **PARK** = Ads API create, TikTok API, MMM, Gate D

## F0 scope (następna sesja — implementacja)

| # | Task |
|---|------|
| 1 | SQLite migrations: `marketing_raw_ingest`, `marketing_facts`, `data_quality_flags`, `order_margin_facts` |
| 2 | `agent/marketing/dtl/` — ingest GA4, orders, leads, L0 probe, margin v1 |
| 3 | Attribution L1-L2 stitch (UTM → session → order) |
| 4 | Commander **Data Health** panel (minimal — facts freshness, quality flags) |
| 5 | pytest fixtures — **nie** fake prod metrics |
| 6 | DoD: 7d ingest design ready + local smoke; VPS deploy tylko na GO |

## Równolegle (Dowódca)

[META-PACK-LEAN.md](../ops/marketing/META-PACK-LEAN.md) — Events InitiateCheckout+Purchase, Audience exclude, master_reel, Leads €10/d.

## PARK / Hard STOP

Gate D · Mollie LIVE · Ads API · TikTok C1-01 · fake PASS · deploy bez GO

## Następna sesja

```
/vibe-init → GO MKT-BRAIN-PRO F0
```

SoT: `docs/ops/marketing/MKT-BRAIN-PRO.md` §5 F0
