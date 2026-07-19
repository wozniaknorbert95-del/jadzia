# Handoff: COI Commander v3 — F0 Workshop PROOF (2026-07-09)

**Plan:** `docs/design/coi-commander/COI-COMMANDER-PLAN-v3.md` — **APPROVED**  
**Gate:** `COI-CMD-WORKSHOP` → **DONE**  
**Prod:** https://api.zzpackage.flexgrafik.nl/commander/

---

## Dowódca sign-off (2026-07-09)

| Test | Wynik |
|------|-------|
| JWT + dashboard Home/queue | ✅ |
| TG `/ticket` + link na telefonie | ✅ (po fix deeplink `1b97201`) |
| Home ≤7 chunków | ✅ |
| Delegat email | ✅ `wozniaknorbert95@gmail.com` (`delegat_configured: true`) |
| Audyt / undo60 | ✅ (per Dowódca) |

---

## Uwagi

- Stare hot_leady `deploy02-*` w kolejce — E2E testy, backlog `COI-CMD-QUEUE-CLEAN`
- Email eskalacji wymaga SMTP na VPS — backlog `COI-CMD-SMTP-01` (brak `SMTP_*` w `.env`)
- Test „3d offline → Delegat” — odłożony (logika w `escalation.py`)

---

## Następny krok

**Dowódca:** codzienny loop — Marketing → approve → publish (poniedziałek rano)  
**Agent:** SMTP eskalacji albo cleanup kolejki E2E
