# F0 Workshop Checklist (2h)

## Wejście

- [x] AUDYT-HIL-KONTROLA.md przeczytany
- [x] AUDYT-V2-GAP.md przeczytany
- [x] UX-BRIEF-COMMANDER.md
- [x] Prod deploy PROOF (`docs/handoffs/2026-07-09-coi-commander-deploy-PROOF.md`)
- [x] `bash deployment/commander-prod-smoke.sh` automated section

## 5 testów

1. **Odwracalność** — public unpublish vs internal 60s undo — _opcjonalnie pominięte (brak published posta)_
2. **Czy ktoś słucha** — Dowódca 3d offline → Delegat push — _odłożone (wymaga 3d; logika w kodzie)_
3. **Obciążenie** — Home wireframe ≤7 chunków — [x] Dowódca 2026-07-09
4. **Poniedziałek rano** — dashboard only flow do FB publish — [x] dashboard + JWT OK
5. **No-laptop** — telefon + signed link → ticket approve — [x] workaround + link fix `1b97201`

## Deliverables sign-off

- [x] D0.1–D0.14 approved on paper (plan v3 APPROVED + prod proof)
- [x] Scorecard draft ≥ acceptable (6/6 closure)

## Notatki sesji

- Delegat email prod: `wozniaknorbert95@gmail.com` (`delegat_configured: true`)
- Deeplink bug: localhost → fix `get_public_base_url()`
- Hot leady `deploy02-*` = stare E2E — do wyczyszczenia w osobnej sesji
