# Handoff — CMD-DASH-UX-POLISH-01 → DEPLOY session

**Date:** 2026-07-22  
**Session verdict:** SUCCESS — LIVE @ `4aea17c`  
**PR:** https://github.com/wozniaknorbert95-del/jadzia/pull/15 — **MERGED** @ `4aea17c`  
**Prod tip LIVE:** `4aea17c` · UI `?v=mkt-dash06`  
**EXPECTED_SHA:** `4aea17c`  
**Phases 0–3:** DONE 2026-07-22 — see `2026-07-22-CMD-DASH-UX-POLISH-01-DEPLOY-CLOSE.md`  
**standing_go_closeout:** `false`

---

## DONE

- Merge #15 · GO deploy · SQLite backup · ff-only pull · restart · VERIFY_OK
- Dogfood H1/H2/touch44/Audyt PASS
- Tip-sync docs + DEPLOY-CLOSE

## LEFT

1. Optional phone 60s dogfood (physical)
2. HITL parks: H-Meta / H-Insights / Mollie (nie ten ticket)
3. Low L1/L2 — nie blokuje

## RISKS

| Risk | Mitigation |
|------|------------|
| Merge bez GO / agent deploy bez GO | Hard STOP Zasada 11 |
| Pull fail / dirty `/opt/jadzia` | `git status` przed pull; tylko `--ff-only` |
| SQLite corruption | backup `.backup` przed restart |
| Stary SW/cache | hard refresh `?v=mkt-dash06` + ctrl+shift+R |
| UX regresja H1/H2 | dogfood checklist poniżej — FAIL = rollback tip |
| JWT / mint na VPS | `sudo -u jadzia … scripts/jwt_token.py` — nie commituj tokenu |

## V-FILES (następna sesja)

1. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\handoffs\2026-07-22-CMD-DASH-UX-POLISH-01-DEPLOY.md` (ten plik)
2. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\ops\COMMANDER-UX-AUDIT-2026-07-22-REAUDIT.md`
3. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\.agents\workflows\jadzia-deploy.md`
4. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\deployment\mkt-dash01-verify.sh`

---

## PLAN DEPLOY KOMPLEKSOWY (sesja następna)

**TASK_ID:** `CMD-DASH-UX-POLISH-01-DEPLOY`  
**1-1-1:** tylko deploy + verify + tip-sync docs — zero feature creep.

### Phase 0 — Preflight (lokalnie, przed GO)

- [x] `gh pr view 15` — CI green / MERGEABLE
- [x] `gh pr checks 15` — all PASS (lint/secrets/test/typecheck/security)
- [x] Merge PR #15 do `master` → merge commit `4aea17c`
- [x] `git fetch origin master && git rev-parse --short origin/master` → **EXPECTED_SHA=`4aea17c`**
- [x] Tip: `index.html` ma `mkt-dash06` ×2 (css+js), brak `mkt-dash05` w HTML
- [x] Jawne GO Dowódcy: „Go deply” → `GO deploy 4aea17c`

### Phase 1 — VPS (tylko po GO)

Host SoT (z poprzednich deployów): `root@185.243.54.115` · key `~/.ssh/cyberfolks_key` · runtime `/opt/jadzia`

```bash
# 0) SSH
ssh -i ~/.ssh/cyberfolks_key root@185.243.54.115

# 1) Pre-state
cd /opt/jadzia
git rev-parse --short HEAD          # PREV_SHA (rollback)
systemctl is-active jadzia
git status --short                  # must be clean for ff-only

# 2) SQLite backup (zawsze)
sudo -u jadzia sqlite3 /opt/jadzia/data/jadzia.db \
  ".backup '/opt/jadzia/data/jadzia-pre-ux-polish-$(date +%Y%m%d-%H%M%S).db'"

# 3) Pull tip
git fetch origin master
git pull --ff-only origin master
TIP=$(git rev-parse --short HEAD)
echo "TIP=$TIP"                     # must equal EXPECTED_SHA

# 4) Deps (runtime UI-only — zwykle no-op; zachowaj rytuał)
sudo -u jadzia bash -lc 'cd /opt/jadzia && source venv/bin/activate && if [ -f requirements.lock ]; then pip install --require-hashes -r requirements.lock -q; else pip install -r requirements.txt -q; fi'

# 5) Restart + health
systemctl restart jadzia
sleep 4
systemctl is-active jadzia
curl -sf http://127.0.0.1:8000/health

# 6) Verify script (SoT cache + rails)
bash deployment/mkt-dash01-verify.sh
# Expect: TIP=EXPECTED_SHA · mkt-dash06 count ≥ 2 · phase-c-cards = 0 · actions/execute = 0
```

### Phase 2 — Browser dogfood (prod)

URL: `https://api.zzpackage.flexgrafik.nl/commander/?v=mkt-dash06`

| # | Check | Pass |
|---|--------|------|
| 1 | Start summary **nie** zawiera `Worker freshness:` literal | |
| 2 | Chip **Freshness** widoczny; summary ≡ worst chip | |
| 3 | Marketing: `PREFLIGHT N/A` + `runtime: propose` (nie critical NO) | |
| 4 | Brak execute UI MB | |
| 5 | Mobile nav touch ≥ 44px (`--touch`) | |
| 6 | Audyt secondary → Weryfikuj → PASS | |
| 7 | Organic KPI: „Brak insights” (nie raw enum overflow) | |

**Hard STOP dogfood:** nie Potwierdź hot_lead · nie publish/cofaj FB.

### Phase 3 — Tip-sync docs (po PASS dogfood)

- Update `OPERATOR-TODAY.md` — tip LIVE + `mkt-dash06` confirmed
- Append tip do CLOSE / ten plik: `LIVE @ <EXPECTED_SHA>`
- `todo.json`: note LIVE; `next_human` = Meta parks HITL / observe
- Handoff CLOSE deploy: `docs/handoffs/YYYY-MM-DD-CMD-DASH-UX-POLISH-01-DEPLOY-CLOSE.md`

### Phase 4 — Rollback (jeśli dogfood FAIL)

```bash
cd /opt/jadzia
git checkout <PREV_SHA>
systemctl restart jadzia
sleep 4
curl -sf http://127.0.0.1:8000/health
# hard refresh ?v=mkt-dash05 (stary cache) lub aktualny hash z PREV tip
```

---

## NEXT_COMMAND_FOR_NEW_AGENT

Deploy CLOSED. Next: `docs/handoffs/2026-07-22-CMD-DASH-UX-POLISH-01-DEPLOY-CLOSE.md` → TASK `OPS-FB-TOKEN-01` (HITL) lub `OPS-FRESHNESS-01` (agent).
