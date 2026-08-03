---
gate: DEMAND-OS-MARKETING-4-00 · agents MASTER-TODO-7 (verify+hardening)
date: 2026-08-03
scope: tool-only · live marketing PARKED
---

# Handoff — MASTER-TODO-7: weryfikacja 6-xx + hardening (DONE 10/10)

## Metoda

Druga iteracja cyklu: **najpierw weryfikacja poprzedniej 10-ki**, potem naprawy, potem ship.
Ad-hoc skrypt audytowy (11 checków edge-case) → rejestr defektów → fixy z testami
regresyjnymi → rozliczenie pre-existing failures do zera → dogfood lokalny+VPS → ship.

## Defekty poprzedniej 10-ki (znalezione w 7-01, wszystkie naprawione)

- **D1** Heartbeat manual-only = martwy mechanizm → auto-heartbeat po udanym `dispatch()`
  (best-effort, warning log; fail/unknown nie zapisuje). Test: `test_dispatch_records_auto_heartbeat`.
- **D2** `hub agents flow --channel myspace` wywalał CLI tracebackiem (`UtmLockError`)
  → `run_hub_spoke_flow` ma teraz wrapper never-raises (`error=flow_exception` + `error_detail`). Test regresyjny.
- **D3** `flow --apply` dla tego samego `asset_id` na 2 kanałach nadpisywał slot pierwszego
  kanału (match tylko po asset_id) → `set_slot_status(..., channel=)` + flow przekazuje channel.
  Test: `test_flow_calendar_bind_is_per_channel` (2 sloty: tiktok + facebook).

## Pre-existing failures → 0

| Test | Przyczyna | Naprawa |
|------|-----------|---------|
| `test_dependencies` JWT x2 | K3 dodał `request` do `verify_jwt`, test nie | bare-request mock (bez cookie) |
| `test_facebook_publish::wrong_platform` | TikTok publish (M2) świadomie rozszerzył kontrakt | seed wiersza `instagram` bezpośrednio (db_create odrzuca unknown) + nowy test `tiktok_needs_token` |
| `test_chat_locale::opening_default_nl`, `at_chat_02` | literalne copy z `flexgrafik-inspire` brain rotuje poza repo | kotwica strukturalna `missing_fields` |
| `quick_previews…` | engine przeszedł na golden path v6.1 (previews na turze vehicle+logo) | test przepisany na v6.1 przez HTTP bridge (real PNG przez PIL) |
| `test_generate_resolves_empty_sku` (429) | cost lock 1 hit/IP/h w persystowanym store | fixture: `DA_RATE_STORE_PATH` tmp + `clear_store()` per test |

**Efekt: pełna `tests/unit` = 688 passed, 16 skipped, 0 failed — pierwszy raz w cyklu.**

## Dogfood

- Desk tile (browser, lokalny dev app): 9 wierszy, chips `brama live`/`narzędzie`,
  `bieg: 2026-08-03` z auto-heartbeat, API 200, public endpoint auth-gated.
- VPS flow: DRY calendar skipped · APPLY slot added · per-channel 2 sloty ·
  INVALID=`flow_exception` · auto-hb zapisany · tmp paths cleaned.

## Porządek

- `agent/inspire/offerte_service.py` (WIP T-012 analytics forwarding, fail-safe) — domknięte
  testem `test_create_offerte_analytics_fail_safe`, idzie w commicie.
- `AGENTS-HEARTBEAT.json` → `.gitignore` (runtime per-env state).
- Untracked świadomie zostają: `assets/tt-upload/*.mp4` (binarny asset), `logs/agent.log`
  (już ignorowany), `.superpowers/sdd/*` (inny workflow), 5F handoffy/dane operacyjne
  (osobny commit danych — poza tym shipem).
- Coverage agents modules po hardeningu: **90% total, min 82%** → K12 artifacts regenerowane.
- Desk UI bez zmian → cache `desk-dash12` zostaje (brak zbędnego bumpu).

## RECOMMENDED_NEXT (tool)

1. Kolejna iteracja cyklu: weryfikacja tej 10-ki na VPS po deploy (owner-verify + dogfood spot-check).
2. Worker loop per rola (design przed kodem) → dopiero wtedy `shell:false` w registry.
3. Dane operacyjne 5F/demand-os w working tree — osobny data-commit albo świadome porzucenie.
4. GA4 live: credentials na VPS + `DEMAND_OS_GA4_LIVE=1` — po GO Dowódcy.
