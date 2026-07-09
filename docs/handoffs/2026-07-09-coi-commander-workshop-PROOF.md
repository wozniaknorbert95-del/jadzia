# Handoff: COI Commander v3 — F0 Workshop PROOF (2026-07-09)

**Plan:** `docs/design/coi-commander/COI-COMMANDER-PLAN-v3.md` — **APPROVED**  
**Gate:** `COI-CMD-WORKSHOP`  
**Prod:** https://api.zzpackage.flexgrafik.nl/commander/

---

## Automated prep (agent)

| Item | Status |
|------|--------|
| Plan v3 status → APPROVED | Done |
| IMPLEMENTATION STATUS section | Done |
| `deployment/commander-prod-smoke.sh` workshop section | Done |
| Closure program sprints S0–S7 | In progress |

---

## Workshop 5 tests (Dowódca — human sign-off)

| # | Test | Automated | Human |
|---|------|-----------|-------|
| 1 | Odwracalność public unpublish vs internal 60s undo | API unpublish OK | Undo UI po S3 |
| 2 | Dowódca offline → Delegat push | Escalation worker S2 | Simulate 24h |
| 3 | Home ≤7 chunków | UI structure | Visual check |
| 4 | Poniedziałek rano dashboard flow | Smoke 7/7 | Walkthrough |
| 5 | No-laptop signed link | Deeplink mint OK | TG `/ticket` na telefonie |

---

## D0.1–D0.14 sign-off

- [x] Specs committed in `docs/design/coi-commander/`
- [x] Backend MVP deployed prod
- [ ] Live TG `/ticket` proof (Dowódca)
- [ ] Scorecard draft ≥ acceptable on paper

---

## Next gate

S1 → S7 closure per plan. Active: `coi_commander_v3_closure`.
