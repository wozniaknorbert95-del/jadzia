# PLAN-DEPLOY-INT-004 — Receiver + gate closure (jadzia-core)

**Status:** ACTIVE  
**Canonical deploy plan (sender + git + tests):** `app.flexgrafik.nl/docs/plans/PLAN-DEPLOY-INT-004.md`  
**Proof handoff:** `docs/handoffs/2026-06-26-deploy-int-004-proof.md`

---

## Role jadzia-core

Receiver INT-004 jest **już na prod** (`POST /api/v1/leads`, `LEADS_API_KEY`, tabela `leads`).

Ten repo domyka tylko: **docs, todo, regresja testów** — bez nowego deployu kodu.

---

## Gate checklist (receiver side)

- [x] `api/routes/leads.py` + `agent/nodes/lead_node.py` na VPS
- [x] `LEADS_API_KEY` w `/root/jadzia/.env`
- [x] Smoke direct API → `sync_status: success`
- [x] Smoke zzpackage `fg_jadzia_sync_lead` → row w DB
- [ ] Browser E2E (sender deploy) — patrz plan app §3.3
- [ ] Duplicate email test — patrz plan app §3.4

---

## Git (jadzia-core)

**Commit scope:**

```
todo.json
docs/handoffs/2026-06-26-deploy-int-004-proof.md
docs/plans/PLAN-DEPLOY-INT-004.md
```

**Nie mieszać** z `docs/handoffs/2026-06-26-coi-docs-alignment.md` — osobny commit docs.

```powershell
cd jadzia-core
pytest tests/unit/test_leads_api.py tests/unit/test_lead_node.py tests/unit/test_lead_store.py -q
git add todo.json docs/handoffs/2026-06-26-deploy-int-004-proof.md docs/plans/PLAN-DEPLOY-INT-004.md
git commit -m "docs(coi): DEPLOY-02 INT-004 plan and proof"
git push origin master
```

Po pełnym browser E2E: uzupełnij proof handoff i ustaw INT-004 → **LIVE** w `flexgrafik-meta`.

---

## Weryfikacja prod (copy-paste)

```bash
# SSH jadzia VPS
sqlite3 /root/jadzia/data/jadzia.db "SELECT COUNT(*) FROM leads;"
sqlite3 /root/jadzia/data/jadzia.db \
  "SELECT id,email,source,game_score,reward_tier,created_at FROM leads ORDER BY id DESC LIMIT 5;"
```

---

## Rollback

Wyłączenie sync po stronie zzpackage (`FG_JADZIA_LEADS_*`) — jadzia bez zmian.
