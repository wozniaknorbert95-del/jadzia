# Worker journal evidence — 2026-08-05

- host: `vps41619215` · unit: `demand-os-agents-worker.service` · since: `today`
- wygenerowano: 2026-08-05T16:22:40+00:00 przez `tools/demand_os_worker_journal_export.py`

## Summary

| Metryka | Wartość |
|---------|---------|
| ticków (Started) | 38 |
| service failures | 0 |
| run-due envelopes | 38 |
| dispatched total | 4 |
| errors total | 0 |

## Per role/action

| role/action | dispatched | error | dry_run |
|-------------|-----------|-------|---------|
| sales/list_hot | 2 | 0 | 0 |
| sales/sync_hot | 2 | 0 | 0 |

## Error lines (max 20)

- brak

## Raw tail

```text
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "ok": true,
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "mode": "apply",
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "due": [],
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "runs": [],
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "dispatched": 0,
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "errors": 0,
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "cadence_roles": [
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:     "cre",
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:     "growth_lead",
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:     "icp_brain",
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:     "sales",
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:     "validator"
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   ],
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T16:29:09+02:00 vps41619215 python[2210564]: }
2026-08-05T16:29:09+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T16:29:09+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
2026-08-05T16:44:13+02:00 vps41619215 systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]: {
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "ok": true,
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "mode": "apply",
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "due": [],
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "runs": [],
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "dispatched": 0,
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "errors": 0,
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "cadence_roles": [
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:     "cre",
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:     "growth_lead",
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:     "icp_brain",
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:     "sales",
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:     "validator"
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   ],
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T16:44:13+02:00 vps41619215 python[2214144]: }
2026-08-05T16:44:13+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T16:44:13+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
2026-08-05T16:59:14+02:00 vps41619215 systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]: {
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "ok": true,
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "mode": "apply",
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "due": [],
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "runs": [],
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "dispatched": 0,
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "errors": 0,
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "cadence_roles": [
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:     "cre",
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:     "growth_lead",
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:     "icp_brain",
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:     "sales",
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:     "validator"
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   ],
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T16:59:14+02:00 vps41619215 python[2217737]: }
2026-08-05T16:59:14+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T16:59:14+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
2026-08-05T17:14:14+02:00 vps41619215 systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]: {
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "ok": true,
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "mode": "apply",
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "due": [],
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "runs": [],
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "dispatched": 0,
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "errors": 0,
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "cadence_roles": [
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:     "cre",
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:     "growth_lead",
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:     "icp_brain",
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:     "sales",
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:     "validator"
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   ],
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T17:14:14+02:00 vps41619215 python[2221314]: }
2026-08-05T17:14:14+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T17:14:14+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
2026-08-05T17:29:14+02:00 vps41619215 systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]: {
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "ok": true,
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "mode": "apply",
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "due": [],
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "runs": [],
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "dispatched": 0,
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "errors": 0,
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "cadence_roles": [
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:     "cre",
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:     "growth_lead",
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:     "icp_brain",
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:     "sales",
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:     "validator"
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   ],
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T17:29:14+02:00 vps41619215 python[2224878]: }
2026-08-05T17:29:14+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T17:29:14+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
2026-08-05T17:44:49+02:00 vps41619215 systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]: {
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "ok": true,
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "mode": "apply",
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "due": [],
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "runs": [],
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "dispatched": 0,
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "errors": 0,
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "cadence_roles": [
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:     "cre",
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:     "growth_lead",
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:     "icp_brain",
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:     "sales",
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:     "validator"
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   ],
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T17:44:50+02:00 vps41619215 python[2229308]: }
2026-08-05T17:44:50+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T17:44:50+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
2026-08-05T17:59:59+02:00 vps41619215 systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]: {
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "ok": true,
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "mode": "apply",
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "due": [],
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "runs": [],
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "dispatched": 0,
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "errors": 0,
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "cadence_roles": [
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:     "cre",
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:     "growth_lead",
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:     "icp_brain",
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:     "sales",
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:     "validator"
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   ],
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T17:59:59+02:00 vps41619215 python[2232922]: }
2026-08-05T17:59:59+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T17:59:59+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
2026-08-05T18:15:13+02:00 vps41619215 systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]: {
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "ok": true,
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "mode": "apply",
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "due": [],
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "runs": [],
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "dispatched": 0,
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "errors": 0,
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "cadence_roles": [
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:     "cre",
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:     "growth_lead",
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:     "icp_brain",
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:     "sales",
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:     "validator"
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   ],
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]:   "note": "tool-only loop \u2014 live_gated roles never dispatched here"
2026-08-05T18:15:13+02:00 vps41619215 python[2236712]: }
2026-08-05T18:15:13+02:00 vps41619215 systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T18:15:13+02:00 vps41619215 systemd[1]: Finished demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch).
```
