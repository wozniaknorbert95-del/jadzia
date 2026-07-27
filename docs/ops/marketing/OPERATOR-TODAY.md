---
status: "[ACTIVE]"
title: "Marketing OS — START TUTAJ (operator)"
updated: "2026-07-27 (GTM v2 expert · NEXT Meta final checklist)"
---

# START TUTAJ — jedna ścieżka (ADHD)

**Priorytet teraz:** **Meta „final”** — [META-FINAL-CHECKLIST](./META-FINAL-CHECKLIST.md) → [META-CLICK-PATH](./META-CLICK-PATH.md) → publish €10/d.  
**GTM SoT:** [GTM-1PAGER.md](./GTM-1PAGER.md) — ICP · offer · WA bridge · **Meta #1** · TT #2 · KPI.  
**Meta organic:** [FREE-META-90.md](./FREE-META-90.md) — **CLOSED 9/10** (IG usunięte). Kampanie HOLD until **„final”**.  
**TikTok system:** [FREE-TIKTOK.md](./FREE-TIKTOK.md) — kod **5/7** · E2E **po** Meta final + asset cadence.  
**Roadmapa:** [MKT-BRAIN-PRO.md](./MKT-BRAIN-PRO.md) — **~86%** overall · runtime **100%** · **MB_MODE=propose**  
**Commander cockpit:** https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08  
**Prod SoT tip:** VPS `/opt/jadzia` **`92da711`** · cache **`mkt-dash08`** · FB Page + `read_insights` + **`pages_read_user_content` LIVE** · SLA `@6e4a637`  
**Kanały:** [FREE-TIKTOK.md](./FREE-TIKTOK.md) · [FREE-META-90.md](./FREE-META-90.md) · [META-CLICK-PATH.md](./META-CLICK-PATH.md) (po „final”) · [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md)

| Co | Status |
|----|--------|
| **GTM-1PAGER** | **LOCKED** — [GTM-1PAGER.md](./GTM-1PAGER.md) |
| **#1 Meta lean** | **NEXT** — [META-FINAL-CHECKLIST](./META-FINAL-CHECKLIST.md) → publish €10/d |
| **FREE-META-90** | **CLOSED 9/10** · IG out of scope · organic utrzymanie |
| **FREE-TIKTOK** | **5/7** · E2E **#2** po Meta final + cadence · no Studio spam |
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

1. **H-Meta** — **NEXT** [META-FINAL-CHECKLIST](./META-FINAL-CHECKLIST.md) → A1–A3 → publish €10/d · 7d hold
2. **H-FREE-META** — **CLOSED 9/10** · organic utrzymanie ([FREE-META-90](./FREE-META-90.md))
3. **H-FREE-TIKTOK** — **#2** po Meta final + cadence · token VPS + E2E ([FREE-TIKTOK](./FREE-TIKTOK.md))
4. **H-GTM** — **DONE** ([GTM-1PAGER](./GTM-1PAGER.md) · [handoff](../../handoffs/2026-07-27-GTM-1PAGER-CLOSE.md))
5. **H-Purchase** — Mollie GO → Test Events Purchase (poza 90%)
6. **H-Insights** — **DONE 2026-07-25** (Page + `read_insights`); F1 = `pages_read_user_content`
7. **H-WA** — Lead → WA &lt;15 min ([SPEED-TO-LEAD](./SPEED-TO-LEAD.md)) · też S10 organic
8. **H-F4x** — distribution / blog / lead webhook — po triggerach

## Operator (Telegram)

1. Karty MB w propose — scoruj / APPROVE gdy sensowne.
2. APPROVE = ticket paste-ready (nie Ads API create).
3. Co tydzień: draft scorecard w TG / Commander (bez auto HOLD/KILL).

### Meta (#1 NEXT — po „final”)

`zzp_branding_check_v1` · **€10/dzień** · camp `120254517992840360` · [GTM-1PAGER](./GTM-1PAGER.md) · [META-FINAL-CHECKLIST](./META-FINAL-CHECKLIST.md) · [META-PACK-LEAN](./META-PACK-LEAN.md).

**„Final” =** checklist P+O+X odhaczony + świadome Purchase PARK + real bus Reel (lub static fallback).

**Zakaz:** Ads API create · Mollie LIVE · fake PASS · reorder STATUS BOARD bez GO · kampanie bez **„final”**.
