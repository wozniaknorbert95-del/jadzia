# Handoff — COI-CONTENT-INTAKE-M2-DEPLOY PROOF

**Date:** 2026-07-17  
**Commit:** `c7338c9` (`origin/master`)  
**VPS:** `/opt/jadzia` @ `c7338c9` — `jadzia` **active**  
**Public:** https://api.zzpackage.flexgrafik.nl/commander/ — health 200, option **Wideo** present

---

## DONE

| Step | Result | Proof |
|------|--------|-------|
| pytest `tests/unit` | **257 passed**, 10 skipped | local preflight |
| Commit + push | `1d46877..c7338c9` | GitHub `master` |
| VPS `git pull` | fast-forward to `c7338c9` | SSH |
| DB backup | `data/jadzia.db.bak.20260717-pre-m2-deploy` | VPS |
| `systemctl restart jadzia` | **active**, health 200 | SSH + public curl |
| Code on VPS | `publish_video` present | `grep` facebook.py:81 |
| UI Marketing | „Wideo” (no M2 queue label) | commander HTML |
| E2E A — MIME gate | **PASS** HTTP 400 | image Drive URL as `content_type=video` |
| E2E B — Graph `/videos` | **REACHED** then **FAIL** | token expired |

---

## E2E detail

### A — MIME gate (PASS)

```
POST /api/v1/content-calendar content_type=video + image GDrive URL
→ 400 "Plik nie wygląda na wideo — sprawdź link lub typ treści (MP4)"
```

### B — Graph video publish (BLOCKED — FB token)

- Entry `id=17` `content_type=video` → status `failed`
- Graph called: `POST https://graph.facebook.com/v25.0/{page_id}/videos` (correct M2 path)
- Error: OAuth `code=190` / `subcode=463` — **Session expired 2026-07-09 11:00 PDT**
- Operator message: `Token Facebook wygasł — odśwież Page Token FlexGrafik`

**Scripts:**
- `deployment/deploy-m2-video-e2e.sh` (bash, needs `M2_TEST_GDRIVE_URL`)
- `deployment/run-m2-video-e2e.py` (prod runner used 2026-07-17)

**Retry after token rotation:**

```bash
ssh root@185.243.54.115
cd /opt/jadzia
# after FB_ACCESS_TOKEN refreshed per docs/ops/FB-TOKEN-ROTATION.md
PYTHONPATH=/opt/jadzia python3 deployment/run-m2-video-e2e.py
# optional GDrive: M2_TEST_GDRIVE_URL='https://drive.google.com/file/d/.../view' \
#   PYTHONPATH=/opt/jadzia python3 deployment/run-m2-video-e2e.py
```

---

## Gate status

| Item | Status |
|------|--------|
| M2 **code** | LIVE on prod |
| M2 **deploy** | **COMPLETE** |
| M2 **live FB video post** | **BLOCKED** — expired Page Token |
| Next human | FB token rotation (`docs/ops/FB-TOKEN-ROTATION.md`) → re-run E2E B |
| Next agent | After token OK: retry E2E OR `/vibe-init` → `DA-INSIRE-ENTERPRISE-MERGE` |

---

## LEFT

| ID | Owner | Note |
|----|-------|------|
| FB token rotacja | **human** | Blocks all FB publish (text/photo/video) |
| M2 E2E B retry | agent | After new token → `fb_post_id` proof |
| DA-INSIRE-ENTERPRISE-MERGE | agent | Blast ready — osobna sesja |
| COI-CMD-SMTP-01 | human+agent | secrets |
| VPS stash `vps-pre-queue-clean-20260717` | Dowódca | keep |

---

## Rollback

```bash
cd /opt/jadzia
git reset --hard 1d46877
systemctl restart jadzia
```

---

```
SESSION_VERDICT: PARTIAL_SUCCESS
DEPLOY: PASS @ c7338c9
E2E_MIME: PASS
E2E_GRAPH_VIDEO: BLOCKED (FB token expired 2026-07-09)
NEXT: human FB-TOKEN-ROTATION → agent E2E retry / DA-INSIRE merge
```
