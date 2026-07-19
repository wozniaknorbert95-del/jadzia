---
status: "[ACTIVE]"
title: "Marketing OS — START TUTAJ (operator)"
updated: "2026-07-19 (CMD-MKT-DASH-02 tip polish)"
---

# START TUTAJ — jedna ścieżka (ADHD)

**Roadmapa:** [MKT-BRAIN-PRO.md](./MKT-BRAIN-PRO.md) — **~86%** overall · runtime **100%** · **MB_MODE=propose**  
**Handoff:** [PROGRAM-CLOSE](../../handoffs/2026-07-19-MKT-BRAIN-PRO-PROGRAM-CLOSE.md) · [DASH-02](../../handoffs/2026-07-19-CMD-MKT-DASH-02.md)  
**Meta:** [META-CLICK-PATH.md](./META-CLICK-PATH.md) · Scorecard: [WEEKLY-SCORECARD.md](./WEEKLY-SCORECARD.md)  
**Commander:** https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash02

| Co | Status |
|----|--------|
| **#1 Meta lean** | **HOLD** — €5; 7d bez edycji |
| Runtime F0→F4b | **100%** LIVE |
| Weekly scorecard draft | **LIVE** w Commander → Marketing |
| Insights agent-half | **READY** — Graph `read_insights` = HITL |
| L0 InitiateCheckout | PASS |
| L0 Purchase | ready_for_human (Mollie) |
| Agent | **observe-only** |

## Commander (Marketing + Analityka)

1. Hard refresh `?v=mkt-dash02` (cache).
2. Zaloguj: TG `/commander` albo Sesja → JWT.
3. **Marketing:** FB strip (amber = brak `read_insights`) · parks H-Meta…H-F4x · weekly draft (Spend/CPL = —).
4. **Analityka → Data Health:** drivers · conscious parks · FB organic reason.
5. Approve MB = **Telegram** (nie ten ekran).

### Troubleshooting

| Objaw | Akcja |
|-------|--------|
| Draft „Sesja wygasła…” / FB „sesja wygasła” | Nowe `/commander` w TG lub świeży JWT |
| Stary cache UI | Hard refresh `?v=mkt-dash02` |
| FB amber + `insights: brak` | H-Insights: Graph scope → `set-fb-access-token` |
| Home ticket „Token Facebook wygasł” mimo FB OK | Stary ticket w kolejce — nie mylić z `fb-health` |

## Twoje parks (HITL)

1. **H-Meta** — hold 7d → optimize ([META-CLICK-PATH](./META-CLICK-PATH.md))
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
