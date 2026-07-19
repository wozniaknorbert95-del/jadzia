# PROOF — COI-CMD-SMTP-01 (SMTP eskalacji Delegata)

**Date:** 2026-07-17  
**Gate:** `COI-CMD-SMTP-01` → **DONE**  
**Local prep:** `master` (uncommitted deliverables — commit when ready)  
**VPS:** `/opt/jadzia` @ `0ef9c67` — `jadzia` **active**  
**Playbook:** `docs/ops/SMTP-DELEGAT-ESCALATION.md`

---

## DONE

| Step | Result |
|------|--------|
| Prep: `.env.example` + playbook + smoke + set-smtp-env | Local + scripts SCP → VPS `/opt/jadzia/deployment/` |
| Gmail App Password (Delegat) | Paste Dowódcy → applied (not in git) |
| VPS `.env` `SMTP_*` | HOST/PORT/USER/FROM set; PASSWORD `***set***` |
| `chown jadzia:jadzia .env` + `chmod 640` | OK |
| `systemctl restart jadzia` | **active** |
| `deployment/smoke-smtp-escalation.py` | **SMTP_SMOKE=PASS** |
| Subject | `[SMOKE] COI Commander SMTP` |
| To (masked) | `w***@gmail.com` |

Kod wysyłki: `agent/commander/escalation.py` → `_send_delegat_email` (bez zmian kontraktu).

---

## LEFT

| Item | Owner | Note |
|------|-------|------|
| Commit+push prep (`.env.example`, playbook, scripts, tests) | Dowódca/agent | lokalnie uncommitted — Zasada 11 / na życzenie |
| Potwierdź INBOX/Spam smoke mail | Dowódca | subject `[SMOKE] COI Commander SMTP` |
| C1-01 TikTok | deferred | poza scope |
| S1-01 BFG | blocked | human |
| Optional: usuń FB test posts / rotacja App Secret | human | higiena |

---

## RISKS / WARNINGS

- **Nie commituj** `SMTP_PASSWORD` / `.env`
- App Password było w czacie — po PROOF OK; przy wycieku publicznym: revoke w Google → nowe hasło
- Eskalacja produkcyjna email tylko gdy Dowódca inactive ≥24h + SLA red (smoke omija ten gate)
- Skrypty na VPS wgrane SCP — po commit+deploy będą też w git tree

---

## V-FILES (next)

1. `todo.json`
2. `docs/handoffs/2026-07-17-coi-cmd-smtp-01-PROOF.md`
3. `docs/ops/SMTP-DELEGAT-ESCALATION.md`

---

```
STATE_SYNC: todo.json + AGENTS.md
HANDOFF_FILE: docs/handoffs/2026-07-17-coi-cmd-smtp-01-PROOF.md
NEXT_SESSION_START: /vibe-init → commit SMTP prep OR next backlog item (nie TikTok bez decyzji)
SESSION_VERDICT: SUCCESS
```
