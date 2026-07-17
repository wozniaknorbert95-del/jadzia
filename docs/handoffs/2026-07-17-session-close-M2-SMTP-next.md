# Handoff — 2026-07-17 session close (M2 video LIVE → SMTP next)

**Branch:** `master` @ `1c5c267`  
**VPS:** `/opt/jadzia` (M2 + DA INSPIRE + FB long-lived PAGE LIVE)  
**Public:** https://api.zzpackage.flexgrafik.nl/commander/

---

## Expert decision — NEXT session

**Najsensowniejsze:** `COI-CMD-SMTP-01` — SMTP na VPS → email eskalacji do Delegata.

**Dlaczego to:**
- Gate już w `todo.json` (`active_gate=COI-CMD-SMTP-01`)
- Kod gotowy: [`agent/commander/escalation.py`](../../agent/commander/escalation.py) (`_send_delegat_email`) — brak tylko `SMTP_*` w `.env`
- Domknięcie Commander v3 (TG działa, email nie)
- Wzorzec jak FB token: agent przygotowuje `.env.example` + playbook + smoke; Dowódca wkleja Gmail app password
- TikTok / D1-03 / secret BFG = gorszy stosunek wartości/ryzyka lub blocked

**Poza scope następnej sesji:** TikTok, BFG secret scrub, drop VPS stash, App Secret re-rotate (opcjonalna higiena).

### Playbook następnej sesji

```text
1. /vibe-init  (V-FILES poniżej)
2. /blast      — COI-CMD-SMTP-01
3. implement   — .env.example SMTP_*; docs/ops SMTP playbook; optional health check endpoint/script
4. STOP        — instrukcja: Gmail app password + SMTP_USER (Delegat)
5. po paste    — zapis VPS .env, restart, smoke eskalacji email
6. /handoff    — PROOF
```

---

## DONE (ta sesja — skrót)

| Item | Proof |
|------|-------|
| M2 video code + deploy | `c7338c9`+ |
| FB long-lived PAGE (`expires_at=0`) | `docs/handoffs/2026-07-17-fb-long-lived-token-PROOF.md` |
| Text+photo smoke | PASS |
| M2 video E2E GDrive | **PASS** entry_id=21 fb_post_id=`1483779380183430` |
| DA INSPIRE enterprise merge+deploy | `46e4fc2` / PROOF |
| Content pipeline text→photo→video | **CLOSED** |

---

## LEFT

| ID | Owner | Note |
|----|-------|------|
| **COI-CMD-SMTP-01** | agent+human | **RECOMMENDED next** |
| C1-01 TikTok | deferred | needs Meta/TikTok program |
| S1-01 secret BFG | blocked | human |
| VPS stash `vps-pre-queue-clean-20260717` | Dowódca | keep |
| Optional: usuń FB test posts | human | text/photo/video smoke |
| Optional: rotate FB App Secret | human | był w czacie |

---

## RISKS / WARNINGS

- Nie commituj `FB_APP_SECRET` / SMTP password / tokenów
- FB App Secret był w czacie — rozważ rotację w Meta (Page token `expires_at=0` zostaje)
- Zasada 11: deploy tylko z approve (w tej sesji było zielone światło)
- Nie mieszaj SMTP z TikTok / INSPIRE w jednej sesji (1-1-1)

---

## V-FILES (max 4) — start SMTP

1. `todo.json`
2. `agent/commander/escalation.py`
3. `docs/handoffs/2026-07-17-coi-content-intake-m2-video-E2E-PROOF.md`
4. `.env.example`

---

```
STATE_SYNC: todo.json + AGENTS.md + brain.md
HANDOFF_FILE: docs/handoffs/2026-07-17-session-close-M2-SMTP-next.md
NEXT_SESSION_START: /vibe-init → COI-CMD-SMTP-01
SESSION_VERDICT: SUCCESS
```
