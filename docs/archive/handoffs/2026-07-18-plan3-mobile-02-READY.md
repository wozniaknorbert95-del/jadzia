# READY — Plan3 COI-CMD-MOBILE-02 (Control Surface)

**Date:** 2026-07-18  
**Repo:** jadzia-core  
**Gate:** `COI-CMD-MOBILE-02`  
**Status:** READY for `@blast`  
**Why now:** Plan dnia (SSoT → phone hub → Demand-04) domknięty; Plan2 **świadomie** odłożył PWA + magic JWT. Cel Dowódcy: **dokończyć dashboard** pod telefon.

## Fundacja (DONE)

| Slice | Status |
|-------|--------|
| Plan1 Control Truth | LIVE |
| Plan2 MOBILE-01 hub | LIVE (`87d7912`) |
| REV-DEMAND F0–F7 | LIVE (`51b3ef0`) |
| Ops close + pre-feature VERIFY | PASS (`e41c519` tip SoT) |

## Cel Plan3 (1-1-1)

Telefon Dowódcy → `/commander/` **używalny end-to-end bez laptopa**:
1. Ścieżka JWT / login na mobile (dogfood Ack `sales_cta` z telefonu)
2. PWA foundation (manifest + service worker minimal — installable)
3. Home nadal hub-not-merge (ADR D0.6); bez rewrite Marketing/Analytics

## STOP

- Gate D / Mollie / min199 / live charge  
- Agent OS merge  
- Kasowanie parków (S1, B3, TikTok, D1, Gate D)  
- Ship `_recover_*.py`  
- Full redesign views

## BLAST start (kolejna sesja)

```text
@blast COI-CMD-MOBILE-02 Plan3 Control Surface

Repo: jadzia-core ONLY | master
Cel: 1-1-1 — mobile JWT dogfood path + PWA install foundation
STOP: bez Gate D; bez merge Agent OS; bez rewrite Marketing/Analytics
Fundacja: Plan1+2 LIVE; Demand-04 LIVE; docs/handoffs/2026-07-18-pre-feature-VERIFY.md
```

## Nota kolejki LIVE

`sales_cta` #4/#5 (`jan@bouw.com` / `bob@gamil.com`) = real HITL — Ack w dogfood Plan3.  
`publish_failed` ×4 = osobny slice (nie blokuje blastu MOBILE-02).
