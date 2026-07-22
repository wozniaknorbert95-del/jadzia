# DEPLOY-READY — OPS-AGENT-SLA-01

**Date:** 2026-07-22  
**Status:** **DEPLOYED LIVE** — superseded by `2026-07-22-OPS-AGENT-SLA-01-DEPLOY-CLOSE.md`  
**Tip LIVE:** `6e4a637` · cache `mkt-dash08`

## Verdict

| Gate | Result |
|------|--------|
| RCA LIVE | PASS — 5 false alarms documented |
| Honesty fix + polish | PASS — DTL newer-wins · HITL `sla_ok=null` · UI `=== false` |
| Unit / UI contract | **26 passed** |
| Secrets / execute UI | PASS — untouched |
| Commit | **not done** — awaits Dowódca GO |
| VPS deploy | **not done** — awaits GO after tip on `origin/master` |

## Deploy-ready polish (this pass)

1. Pipeline clocks: **newer of** `agent_state` vs DTL (stale agent_state cannot mask fresh ingest)
2. UI: drop unused `hasNext` in SLA chip paths
3. Verify script: print `sla_bad` / `sla_na` / `clock_source` for all agents
4. Extra unit: prefers newer DTL · keeps newer agent_state

## Commit scope (1-1-1 — IN)

```text
agent/commander/agents_registry.py
agent/commander/escalation.py
agent/commander/queue.py
commander-ui/app.js
commander-ui/index.html
deployment/mkt-dash01-verify.sh
deployment/_ops_agent_sla_rca.py
tests/unit/test_agents_sla_honesty.py
tests/unit/test_commander_complete_ui.py
docs/handoffs/2026-07-22-OPS-AGENT-SLA-01-CLOSE.md
docs/handoffs/2026-07-22-NEXT-OPS-AGENT-SLA-01.md
docs/handoffs/2026-07-22-NEXT-OPS-AGENT-SLA-01-DEPLOY.md
docs/handoffs/2026-07-22-OPS-AGENT-SLA-01-DEPLOY-READY.md  (this file)
docs/handoffs/README.md
todo.json
.cursor/session-state.md
.gitignore   # .coverage / coverage.xml / htmlcov (noise)
```

## OUT of this commit (leave dirty or separate)

```text
D  .coverage                          # local noise; gitignored after commit
M  docs/handoffs/2026-07-22-OPS-FRESHNESS-01-DEPLOY-CLOSE.md  # prior tip-sync tidy
?? docs/handoffs/2026-07-22-SESSION-HANDOFF.md               # prior session — optional include
```

**Recommendation:** SESSION-HANDOFF can ride along for continuity; FRESHNESS-DEPLOY-CLOSE edit is optional (not SLA). Do **not** commit secrets / JWT.

## Proposed commit message

```text
fix(ops): agent SLA honesty from DTL clocks (mkt-dash08)

Stop Start-rail false 'SLA bad 5' when pipeline is healthy: derive
analytics/sales/operations clocks from DTL, treat marketing/design as
HITL n/a, count only sla_ok===false.
```

## Phase 0 — Preflight (lokalnie, przed GO)

- [x] Scoped pytest PASS (26)
- [x] Cache `mkt-dash08` ×2 in `index.html`; no `mkt-dash07` in HTML
- [x] Hard STOP surfaces clean (no execute UI / no FB token)
- [ ] Dowódca GO: commit (+ PR/merge jeśli wymagane) + deploy VPS

## Phase 1 — COMMAND_BLOCK (tylko po GO)

Host SoT: `root@185.243.54.115` · key `~/.ssh/cyberfolks_key` · `/opt/jadzia`

```bash
# --- LOCAL (agent after GO commit) ---
# 1) Stage IN-scope only, commit, push master (or PR → merge)
# 2) EXPECTED_SHA=$(git rev-parse --short HEAD)

# --- VPS ---
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115

cd /opt/jadzia
PREV_SHA=$(git rev-parse --short HEAD)
systemctl is-active jadzia
git status --short   # must be clean for ff-only

sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-ops-sla-$(date +%Y%m%d-%H%M%S).db'"

git fetch origin master
git pull --ff-only origin master
TIP=$(git rev-parse --short HEAD)
echo "TIP=$TIP PREV=$PREV_SHA"   # TIP must == EXPECTED_SHA

sudo -u jadzia bash -lc 'cd /opt/jadzia && source venv/bin/activate && if [ -f requirements.lock ]; then pip install --require-hashes -r requirements.lock -q; else pip install -r requirements.txt -q; fi'
systemctl restart jadzia
sleep 4
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health

bash deployment/mkt-dash01-verify.sh
# Expect: mkt-dash08 ≥ 2 · sla_bad list empty or only real scheduled breaches · VERIFY_OK
```

## Phase 2 — Browser dogfood (prod)

URL: `https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash08`

| # | Check | Pass |
|---|--------|------|
| 1 | Chip SLA **nie** `bad: 5` bez powodu | |
| 2 | Summary **nie** krzyczy `SLA bad 5` gdy pipeline DTL świeży | |
| 3 | Freshness amber/red nadal widoczne jeśli deserved | |
| 4 | Agenci: marketing/design SLA `n/a`; analytics/sales/ops ok przy DTL | |
| 5 | Brak execute UI MB · brak Potwierdź hot_lead · brak FB publish | |

## Phase 3 — Tip-sync (po PASS dogfood)

- `OPERATOR-TODAY.md` → tip + `mkt-dash08`
- CLOSE deploy: `2026-07-22-OPS-AGENT-SLA-01-DEPLOY-CLOSE.md`
- `todo.json` LIVE note; next = FB deferred / L1L2

## Phase 4 — Rollback

```bash
cd /opt/jadzia
git checkout <PREV_SHA>
systemctl restart jadzia
sleep 4
curl -sf http://127.0.0.1:8000/health
# hard refresh ?v=mkt-dash07
```

## NEXT

```text
Na GO Dowódcy: commit (scope IN) → push → OPS-AGENT-SLA-01-DEPLOY (VPS + dogfood)
SoT: ten plik
```

**DEPLOY_STATUS:** `AWAIT_COMMANDER`  
**RECOMMENDED_NEXT:** GO → commit+deploy  
**HUMAN_CLICKS:** 1 (GO)
