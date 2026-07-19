# BLAST — COI-CMD-SMTP-01 (SMTP eskalacji Delegata)

**Date:** 2026-07-17  
**Backlog:** `COI-CMD-SMTP-01`  
**Branch:** `master` @ `356e3d1`  
**Scope:** env template + ops playbook + smoke. **No** TikTok / INSPIRE / BFG.

---

## B — Background

Commander v3 eskaluje SLA red do Delegata przez TG + email (`agent/commander/escalation.py` → `_send_delegat_email`).  
`delegat_email` jest ustawiony (`wozniaknorbert95@gmail.com`). Brak `SMTP_*` na VPS → email jest skipowany (log: `email skipped`).

**Value:** gdy Dowódca nieaktywny ≥24h i item SLA red → email do Delegata (N6).

**Flow:** worker_loop → `check_sla_escalations()` → TG always → email if inactive + `SMTP_HOST` + `delegat_email`.

---

## L — Limitations

- SMTP optional — brak hosta = skip (nie crash boot)
- Gmail: wymaga **App Password** (2FA), nie zwykłego hasła
- Sekrety tylko VPS `.env` — nigdy git
- Smoke woła `_send_delegat_email` bezpośrednio (nie czeka 24h inactivity)
- Zasada 11: apply + restart tylko po paste Dowódcy

---

## A — Actions

- [x] `.env.example` — `SMTP_HOST/PORT/USER/PASSWORD/FROM`
- [x] `docs/ops/SMTP-DELEGAT-ESCALATION.md` — playbook Gmail + VPS apply
- [x] `deployment/smoke-smtp-escalation.py` — test send bez printu sekretów
- [x] unit: skip bez hosta + send gdy skonfigurowane (4/4 pytest PASS)
- [x] `deployment/set-smtp-env.py` — apply po paste
- [ ] STOP — Dowódca: Gmail app password
- [ ] po paste: VPS `.env` + restart + smoke → `/handoff` PROOF

---

## S — Success Criteria

- [ ] Repo: `.env.example` + playbook + smoke committed (bez sekretów)
- [ ] VPS: `SMTP_HOST=smtp.gmail.com` + user/password set
- [ ] Smoke: `SMTP_SMOKE=PASS` (email w skrzynce Delegata)
- [ ] Prod: restart `jadzia` green; brak sekretów w logach/git

---

## T — Test Plan

| Layer | Co |
|-------|----|
| Unit | `test_send_delegat_email_skipped_without_host`, `test_send_delegat_email_ok` |
| Smoke | `deployment/smoke-smtp-escalation.py` na VPS po apply |
| Manual | Skrzynka Delegata — subject `[SMOKE] COI Commander SMTP` |

---

```
BLAST_ANCHOR: docs/handoffs/2026-07-17-coi-cmd-smtp-01-blast.md
BACKLOG_ID: COI-CMD-SMTP-01
INVARIANTS_TO_PROTECT: escalation.py contract; no secrets in git; TikTok/INSPIRE/BFG untouched
SUCCESS_CRITERIA: smoke PASS + email received
IMPLEMENTATION_PLAN: .env.example → playbook → smoke → STOP secrets → VPS apply

CURRENT_STAGE: L1-Design → L2-Implement (autonomous prep)
RECOMMENDED_NEXT: /implement then STOP
```
