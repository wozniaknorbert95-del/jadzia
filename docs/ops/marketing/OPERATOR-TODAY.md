---
status: "[ACTIVE]"
title: "Marketing OS — START TUTAJ (operator)"
updated: "2026-07-25 (META-FREE-90 9/10 PASS · kampanie HOLD until final)"
---

# START TUTAJ — jedna ścieżka (ADHD)

**Priorytet teraz:** [FREE-META-90.md](./FREE-META-90.md) — **9/10 PASS** · kampanie HOLD until Dowódca **„final”**. Leftover Low: S9 IG.  
**Roadmapa:** [MKT-BRAIN-PRO.md](./MKT-BRAIN-PRO.md) — **~86%** overall · runtime **100%** · **MB_MODE=propose**  
**Commander cockpit:** https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08  
**Prod SoT tip:** VPS `/opt/jadzia` **`92da711`** · cache **`mkt-dash08`** · FB Page + `read_insights` + **`pages_read_user_content` LIVE** · SLA `@6e4a637`  
**Meta:** [FREE-META-90.md](./FREE-META-90.md) · [META-CLICK-PATH.md](./META-CLICK-PATH.md) (po „final”) · [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md)

| Co | Status |
|----|--------|
| **FREE-META-90** | **9/10 PASS** @ tip **`92da711`** · S5 Away+IR ON · S9 Low leftover · kampanie HOLD |
| **#1 Meta lean** | **HOLD** — €5 · **po** Dowódca **„final”** |
| Runtime F0→F4b | **100%** LIVE |
| Weekly scorecard draft | **LIVE** · Organic ER baseline numeric |
| Decision Rail (MB) | **LIVE** — preflight/breakers/accuracy (read-only) |
| Insights + user_content | **LIVE** (META-FREE F1) |
| L0 InitiateCheckout | PASS |
| L0 Purchase | ready_for_human (Mollie) · poza mianownikiem 90% |
| Agent | observe · kampanie tylko po „final” |

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
| FB amber + `insights: brak` | Rare after OPS-FB-TOKEN-01 — rotate via [FB-TOKEN-ROTATION.md](../FB-TOKEN-ROTATION.md) |
| Preflight NO przy MB_MODE=propose | Oczekiwane (preflight = cutover evidence, nie flip) |

## Twoje parks (HITL — poza Commanderem)

1. **H-FREE-META** — **GATE PASS 9/10** · leftover Low S9 IG ([FREE-META-90](./FREE-META-90.md))
2. **H-Meta** — hold → optimize ([META-CLICK-PATH](./META-CLICK-PATH.md)) — **dopiero po** „final”
3. **H-Purchase** — Mollie GO → Test Events Purchase (poza 90%)
4. **H-Insights** — **DONE 2026-07-25** (Page + `read_insights`); F1 = `pages_read_user_content`
5. **H-WA** — Lead → WA &lt;15 min ([SPEED-TO-LEAD](./SPEED-TO-LEAD.md)) · też S10 organic
6. **H-F4x** — distribution / blog / lead webhook — po triggerach

## Operator (Telegram)

1. Karty MB w propose — scoruj / APPROVE gdy sensowne.
2. APPROVE = ticket paste-ready (nie Ads API create).
3. Co tydzień: draft scorecard w TG / Commander (bez auto HOLD/KILL).

### Meta (#1 HOLD)

`zzp_branding_check_v1` · €5/dzień · camp `120254517992840360`.

**Zakaz:** Ads API create · Mollie LIVE · fake PASS · reorder STATUS BOARD bez GO · kampanie bez **„final”**.
