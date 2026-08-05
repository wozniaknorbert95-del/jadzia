# HANDOFF — MT-9 zadanie 9-09: BLOCKING-MODE CANARY (2026-08-05)

**Date:** 2026-08-05, okno **15:38:44 → 15:41:10 UTC (2 min 26 s)**
**Cel:** udowodnić na prod, że alarm staleness naprawdę strzela end-to-end (nie tylko "fresh [blocking]")
**Metoda:** kontrolowany backdate heartbeat 1 roli → doctor RED → owner-verify FAIL → restore → green
**Werdykt:** **PASS** — pełny cykl alarmu potwierdzony na produkcji

## Przebieg (fakty)

| Krok | Dowód |
|------|-------|
| Backup | `sudo -u jadzia cp AGENTS-HEARTBEAT.json /tmp/hb-backup-canary.json` → ok |
| Backdate | `sales.last_run_at` → `2026-07-28T13:27:44+00:00` (−8d; limit sales = 12h) |
| **doctor RED** | `ok:false` · `agents_staleness: "stale: sales(194.2h>12h) — run: tools.demand_os_hub agents run-due --apply [blocking]"` · errors: `['agents_staleness FAIL (blocking mode)']` |
| **owner-verify RED** | exit **1** · `ok:false` · doctor step fail (blocking) |
| **desk footer RED** | `footer_full.doctor_ok: false, doctor_scope: full` — widoczny alarm na desk potwierdzony |
| Restore | `cp` backupu (jadzia) → `sales.last_run_at = 2026-08-05T13:27:44+00:00` |
| **doctor GREEN** | `ok:true` · `"all cadence roles fresh [blocking]"` |
| **owner-verify GREEN** | exit **0** · `ok:true` |

## Uwagi

- **Self-heal nie zdążył:** worker tick nie wypadł w oknie (timer 15 min) — restore z backupu. Gdyby tick wypadł, worker sam by wyleczył heartbeat (też poprawny scenariusz, udokumentowany w MT-9).
- Ownership pliku po cyklu: `jadzia:jadzia` ✓ · `/tmp/hb-backup-canary.json` zostawiony (nieszkodliwy).
- Łańcuch alarmowy potwierdzony: heartbeat stale → doctor RED [blocking] → owner-verify exit 1 → desk footer `doctor_ok:false`.
- Artefakty na VPS: `/tmp/canary-doctor-red.json`, `/tmp/canary-ov-red.json`, `/tmp/canary-doctor-green.json`, `/tmp/canary-ov-green.json`.

## STOP

Canary = jedyna dozwolona manipulacja runtime na prod; okno < 5 min dotrzymane (2:26).
