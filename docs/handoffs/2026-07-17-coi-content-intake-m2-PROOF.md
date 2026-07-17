# Handoff — COI-CONTENT-INTAKE-M2 (Video/Reels z GDrive)

**Date:** 2026-07-17  
**Branch:** `master` (local, pre-deploy)  
**Gate:** `COI-CONTENT-INTAKE-M2` — **CODE COMPLETE**  
**BLAST:** `docs/handoffs/2026-07-17-coi-content-intake-m2-blast.md`

---

## DONE

| Item | Proof |
|------|-------|
| `publish_video(description, file_url)` — Graph `POST /{page_id}/videos` | `agent/publishers/facebook.py` |
| Routing `content_type=video` → `publish_video` | `agent/publishers/calendar_publish.py` |
| Probe + MIME check on create/update for video | `agent/nodes/content_calendar_node.py` |
| UI: opcja „Wideo” aktywna (bez „kolejka M2”) | `commander-ui/index.html` |
| Unit tests M2 + stale publish mocks fixed | 257 pytest PASS |
| Video error PL w `parse_publish_error` | `facebook.py` |

---

## TEST_RESULT

```
TEST_RESULT: PASS
LINT: pre-existing style warnings in touched files (no new blockers)
PYTEST: 257 passed, 10 skipped (full tests/unit)
M2 targeted: 22 passed (facebook_publisher + calendar_media + calendar_publish)
SMOKE_TEST: not run on prod — Zasada 11
```

---

## Deploy checklist (Dowódca — manual approve)

**STOP:** Agent nie wykonywał deploy (Zasada 11).

```bash
# 1. VPS — pull + restart (Dowódca)
ssh jadzia@vps
cd /opt/jadzia
git fetch origin && git checkout master && git pull
sudo systemctl restart jadzia
sudo systemctl status jadzia

# 2. Health
curl -sf https://api.zzpackage.flexgrafik.nl/health

# 3. Commander UI — Marketing
#    - Typ: Wideo
#    - Wklej link MP4 z COI-Marketing (każdy z linkiem)
#    - Zapisz szkic → probe OK
#    - Opublikuj teraz (test) LUB zaplanuj

# 4. Verify FB Page — post wideo widoczny
# 5. Optional cleanup — usuń test post z FB
```

**Env prereqs (already on prod from M1):** `FB_PAGE_ID`, `FB_ACCESS_TOKEN` (Page Token).

**Known limits:** Duży MP4 + GDrive virus-scan interstitial → Meta może nie pobrać; playbook `docs/ops/COI-MARKETING-GDRIVE-SETUP.md` §troubleshooting.

---

## LEFT

| ID | Owner | Note |
|----|-------|------|
| M2 prod E2E | Dowódca | Po deploy checklist powyżej |
| feat/da-insire-enterprise merge | agent (later) | Osobna sesja — nie mieszać |
| COI-CMD-SMTP-01 | human+agent | SMTP secrets |
| FB token rotacja | human | ops hygiene |
| TikTok Phase C | deferred | `todo.json` C1-01 |

---

## RISKS

- GDrive large video → Graph timeout / interstitial (120s timeout w kodzie)
- Reels format — **nie** w scope M2 (zwykły Page video)
- Nie checkout `feat/da-insire-enterprise` podczas deploy M2

---

## NEXT session

```
/vibe-init → feat/da-insire-enterprise review LUB COI-CMD-SMTP-01
```

Albo po deploy M2: Dowódca potwierdza E2E wideo → zamknąć gate w `todo.json`.

---

```
STATE_SYNC: todo.json + AGENTS.md updated
HANDOFF_FILE: docs/handoffs/2026-07-17-coi-content-intake-m2-PROOF.md
NEXT_SESSION_START: Deploy M2 (human) → optional /vibe-init INSPIRE
SESSION_VERDICT: SUCCESS (code + tests; deploy pending Dowódca)
```
