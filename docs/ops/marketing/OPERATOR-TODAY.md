---
status: "[ACTIVE]"
title: "Marketing OS — START TUTAJ (operator)"
updated: "2026-07-22 (OPS-AGENT-SLA LIVE @ 6e4a637 mkt-dash08)"
---

# START TUTAJ — jedna ścieżka (ADHD)

**Roadmapa:** [MKT-BRAIN-PRO.md](./MKT-BRAIN-PRO.md) — **~86%** overall · runtime **100%** · **MB_MODE=propose**  
**Commander cockpit:** https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08  
**Prod SoT tip:** VPS `/opt/jadzia` `git rev-parse --short HEAD` · cache **`mkt-dash08`** · SLA honesty LIVE (`6e4a637`) · freshness `@c210578`  
**Meta:** [META-CLICK-PATH.md](./META-CLICK-PATH.md) · Scorecard: [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md)

| Co | Status |
|----|--------|
| **#1 Meta lean** | **HOLD** — €5; 7d bez edycji |
| Runtime F0→F4b | **100%** LIVE |
| Weekly scorecard draft | **LIVE** w Commander → Marketing |
| Decision Rail (MB) | **LIVE** — preflight/breakers/accuracy (read-only) |
| Insights agent-half | **READY** — Graph `read_insights` = HITL |
| L0 InitiateCheckout | PASS |
| L0 Purchase | ready_for_human (Mollie) |
| Agent | **observe-only** |

## Commander (hub decyzji)

1. Hard refresh `?v=mkt-dash08`.
2. Zaloguj: TG `/commander` albo Sesja → JWT.
3. **Start:** Ops Decision Rail (SSH/SQLite/Loop/SLA/GA4).
4. **Marketing:** L0 Brain rail (GO/WARN/NO + accuracy) · weekly draft · organic HITL.
5. **Analityka:** KPI scoreboard · DTL · tabele orders/leads.
6. **Agenci:** fleet truth + AI OS map (bez fake phase-c).
7. Approve / execute MB = **Telegram lub API** — **nie** przycisk w Commanderze.

### API-only (świadomie poza UI) — ORPHAN-SOT

| Endpoint | Gdzie |
|----------|--------|
| `POST /api/v1/marketing/actions/execute` | Telegram HITL / curl z tokenem |
| Graduation meters / feedback / bulk-approve | TG lub API — nie Commander UI |
| MB cycle / memory sync / eval-score | ops API — osobny HITL ticket |

### Troubleshooting

| Objaw | Akcja |
|-------|--------|
| Draft „Sesja wygasła…” | Nowe `/commander` w TG lub świeży JWT |
| Stary cache UI | Hard refresh `?v=mkt-dash08` |
| FB amber + `insights: brak` | H-Insights: Graph scope → `set-fb-access-token` |
| Preflight NO przy MB_MODE=propose | Oczekiwane (preflight = cutover evidence, nie flip) |

## Twoje parks (HITL — poza Commanderem)

1. **H-Meta** — hold 7d → optimize ([META-CLICK-PATH](./META-CLICK-PATH.md)) — Ads Manager
2. **H-Purchase** — Mollie GO → Test Events Purchase
3. **H-Insights** — Graph `read_insights` → nowy token → `set-fb-access-token`
4. **H-WA** — Lead → WA &lt;15 min ([SPEED-TO-LEAD](./SPEED-TO-LEAD.md))
5. **H-F4x** — distribution / blog / lead webhook — po triggerach

## Operator (Telegram)

1. Karty MB w propose — scoruj / APPROVE gdy sensowne.
2. APPROVE = ticket paste-ready (nie Ads API create).
3. Co tydzień: draft scorecard w TG / Commander (bez auto HOLD/KILL).

### Meta (#1 HOLD)

`zzp_branding_check_v1` · €5/dzień · camp `120254517992840360`.

**Zakaz:** Ads API create · Mollie LIVE · fake PASS · reorder STATUS BOARD bez GO.
