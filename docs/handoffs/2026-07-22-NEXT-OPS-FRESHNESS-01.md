# Next task — post UX-POLISH LIVE

**Date:** 2026-07-22  
**Context tip:** `04e278f` · UX `@4aea17c` · `mkt-dash06` LIVE  
**Prior CLOSE:** `2026-07-22-CMD-DASH-UX-POLISH-01-DEPLOY-CLOSE.md`

## Coherence verdict

| Layer | Status |
|-------|--------|
| VPS HEAD | `04e278f` |
| UI cache | `mkt-dash06`×2 |
| Dogfood H1–H3 / Audyt | PASS |
| OPERATOR-TODAY / todo / CLOSE | tip-sync LIVE |

## Expert pick — jedna ścieżka

**Nie** kontynuuj UI polish (L1/L2 = Low, nie blokuje).  
Polished Ops rail **prawidłowo** krzyczy `freshness red` — to teraz główny sygnał zaufania, nie bug UX.

### NEXT_AGENT (kod / 1-1-1)

```text
TASK_ID: OPS-FRESHNESS-01
REPO: jadzia-core
CLASS: HotFix / BugFix (data pipeline freshness)
```

**Misja:** Przywróć wiarygodność Ops Decision Rail — zdiagnozuj i napraw (lub świadomie parkuj z SLA) **RED** na ORDERS / LEADS / WORKER freshness (sync timestamps z dogfood: orders ~4d, leads ~4d, worker ~2d; GA4 OK).

**DoD (minimal):**
- [ ] Root-cause note (job/cron/API/ingest) z evidence
- [ ] Albo sync restored (chips → nie red bez fake PASS), albo `ready_for_human` park z owner+next step
- [ ] Unit/contract jeśli zmieniasz freshness logic
- [ ] Zero Gate D / Mollie / secrets / execute UI

**Dlaczego to, nie L1/L2:** bez świeżych faktów Commander jest „ładnym alarmem” — nie hubem decyzji.

### NEXT_HUMAN (równolegle, HITL)

```text
TASK_ID: OPS-FB-TOKEN-01  (park H-Insights / Meta)
```

Dogfood pokazał **CRITICAL**: „Token Facebook wygasł”. Odśwież Page Token (+ opcjonalnie Graph `read_insights`) → `set-fb-access-token`. Agent **nie** robi tego autonomicznie (secrets).

## Hard STOP

standing_go_closeout=false · no autonomous VPS bez GO · no fake PASS freshness.
