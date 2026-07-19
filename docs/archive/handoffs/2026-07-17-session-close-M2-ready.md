# Handoff — 2026-07-17 session close (restore footing → M2 ready)

**Branch:** `master` @ `1d46877`  
**VPS:** `/opt/jadzia` @ `1d46877` — `jadzia` active  
**Public:** https://api.zzpackage.flexgrafik.nl/commander/

---

## Expert decision — NEXT session (autonomous)

**Najsensowniejsze działanie:** `COI-CONTENT-INTAKE-M2` — Video/Reels publish z GDrive URL.

**Dlaczego nie INSPIRE merge teraz:**
- `feat/da-insire-enterprise` = +14 commits, stash review pending, split-brain z `v31`
- Wysokie ryzyko regressji vs. wąski, kontynuacyjny tor Marketing (M1 + Phase B już LIVE)
- 1-1-1: najpierw domknąć content pipeline (tekst/foto → wideo), potem DA

**Dlaczego M2 bez Dowódcy w pętli:**
- Gate już ustawiony w `todo.json`
- Kontrakt wzorowany na M1 (`content_type=video`, `publish_calendar_content` dziś zwraca błąd M2)
- Smoke Marketing można zastąpić API/prod inspect (agent), nie UI click-through
- **Zasada 11:** implement + test + PROOF + checklist deploy — **STOP przed `systemctl restart` / prod apply** bez osobnego „go deploy”

### Playbook następnej sesji (agent-only)

```text
1. @vibe-init  (V-FILES poniżej)
2. @explore    — FB Graph video/Reels + GDrive + calendar_publish video stub
3. @blast      — COI-CONTENT-INTAKE-M2 (spec + plan w docs/superpowers/)
4. @implement  — publish_video path, UI Marketing video enable, tests
5. @jadzia-test — pytest targeted suite
6. @handoff    — PROOF + deploy checklist (manual approve)
```

**Poza scope tej sesji:** merge INSPIRE, SMTP, FB token rotacja, drop VPS stash.

---

## DONE (ta sesja)

| Item | Proof |
|------|-------|
| Restore footing F0–F1 | `docs/handoffs/2026-07-17-restore-footing.md` |
| Push / sync `origin/master` | `1d46877` |
| QUEUE-CLEAN prod | deleted 3 E2E; dry-run 0; PROOF file |
| Truth-sync brain/AGENTS/todo | gate → `COI-CONTENT-INTAKE-M2` |
| INSPIRE parked | documented; no mix |

---

## LEFT

| ID | Owner | Note |
|----|-------|------|
| **COI-CONTENT-INTAKE-M2** | agent (next) | Video/Reels — **RECOMMENDED** |
| feat/da-insire-enterprise merge | agent (later) | + stash review |
| Marketing UI smoke | human optional | agent can API-smoke instead |
| FB token rotacja | human | ops hygiene |
| COI-CMD-SMTP-01 | human+agent | needs SMTP secrets |
| VPS stash `vps-pre-queue-clean-20260717` | Dowódca | keep until confirmed safe to drop |

---

## RISKS

- Zasada 11: no autonomous prod deploy
- Video Graph API + GDrive large files — probe/timeouts
- Do not checkout INSPIRE during M2
- Local stash inspire ≠ VPS stash — different concerns

---

## V-FILES (max 4)

1. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\handoffs\2026-07-17-restore-footing.md`
2. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\todo.json`
3. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\agent\publishers\calendar_publish.py`
4. `C:\Users\FlexGrafik\FlexGrafik\github\jadzia-core\docs\superpowers\specs\2026-07-09-coi-content-intake-design.md`
