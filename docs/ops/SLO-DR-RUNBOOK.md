# Jadzia Core — SLO / DR / restore runbook

**Status:** ACTIVE (AUD-REM-OPS-01)  
**Scope:** operations maturity without autonomous deploy  
**Owner:** Dowódca (HITL restore) + agent (docs/scripts)

## Single-process invariant

- Run **one** uvicorn process (`jadzia.service`).
- Do **not** use `--workers N` or multiple systemd instances sharing `data/jadzia.db`.
- Schedulers (FB, marketing, brief) start inside the API process; multi-worker duplicates them.

## SLO (minimum)

| SLI | Target | Error budget |
|-----|--------|--------------|
| `/worker/health` availability | 99% / 30d | measured via external probe or uptime |
| Task failure rate (`errors_last_hour`) | investigate if sustained > 5 | process-local metrics |
| Restart budget | ≤ 5 restarts / 5 min (`StartLimitBurst`) | systemd |

## RPO / RTO

| Metric | Target | Notes |
|--------|--------|-------|
| RPO | ≤ 24 h | daily SQLite backup on VPS + optional off-site copy |
| RTO | ≤ 1 h | restore `.db` backup + `systemctl restart jadzia` |

## Backup policy

1. On VPS before every deploy:
   `sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db ".backup '/opt/jadzia/data/jadzia-pre-deploy-$(date +%Y%m%d-%H%M%S).db'"`
2. Keep ≥7 local backups; copy weekly off-site (HITL).
3. **Never** default-upload local laptop DB onto production (`deploy-to-vps.sh` defaults to **N**).

## Restore drill (HITL evidence)

1. Pick a non-prod or pre-deploy backup.
2. Stop service → restore file → start service.
3. `PRAGMA integrity_check;` → `ok`
4. `curl -sf http://127.0.0.1:8000/worker/health`
5. Record timestamp, tip SHA, exit codes in handoff — required for production PASS.

## Systemd hardening (shipped)

`ProtectSystem=strict`, `ProtectHome`, `PrivateDevices`, `RestrictAddressFamilies`, `ReadWritePaths` for data/logs/venv.

## Deploy contract

```bash
pip install --require-hashes -r requirements.lock
systemctl restart jadzia   # single process
```
