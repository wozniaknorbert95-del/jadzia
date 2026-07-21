# Handoff — MKT-BRAIN-PRO-DH-AMBER CLOSE

**Date:** 2026-07-19  
**Gate:** MKT-BRAIN-PRO  
**Status:** Data Health drivers LIVE · IC ack · Purchase park=info

## Root cause

`overall=amber` napędzał **jeden** flag `l0_pixel_events` / missing:  
„HTML OK — InitiateCheckout/**Purchase** still require Events Manager”.

IC już **PASS**; Purchase = **PARK** (Mollie) — nie powinien trzymać overall amber.

## Fix

- `l0_probe.py`: split IC vs Purchase; `L0_IC_VERIFIED=1` → severity **info**
- `report.py`: `drivers[]`, `conscious_parks[]`, `quality_summary.info`
- info/park **nie** ustawiają overall amber/red

## Progress (board)

| Warstwa | % |
|---------|---|
| Runtime F0→F4b | **100%** |
| Data Health honesty | **95%** |
| Meta lean #1 | **70%** (HOLD €5) |
| L0 events | **50%** (IC PASS / Purchase PARK) |
| **Overall program** | **~82%** |

## Next

Observe cycles · Meta hold · Purchase tylko z Mollie GO · `read_insights` gdy scope
