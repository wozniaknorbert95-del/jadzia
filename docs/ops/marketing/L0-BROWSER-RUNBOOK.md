---
status: "[ACTIVE]"
title: "L0 Browser runbook — agent + Dowódca login"
updated: "2026-07-19"
---

# L0 — plan działania (browser agent)

## Rola

| Kto | Co |
|-----|-----|
| **Agent** | Nawigacja Events Manager, Test Events, Wizard checkout, screenshot evidence, zapis w handoff |
| **Dowódca** | Tylko login FB / 2FA / captcha (gdy agent zatrzyma) |

## Kroki agenta (kolejność)

1. Otwórz `https://business.facebook.com/events_manager2` (visible tab).
2. Cookies → **Allow all** (jeśli modal).
3. **STOP na login** → unlock browser → Dowódca: *Continue with Facebook* + hasło/2FA.
4. Po logowaniu: wybierz dataset **zzpackage / Wizard pixel**.
5. Wejdź w **Test events**.
6. Nowa karta: Wizard `https://zzpackage.flexgrafik.nl/wizard/` → dojście do checkout → sprawdź `InitiateCheckout` w Test Events.
7. Purchase: tylko jeśli możliwy **test/sandbox** bez live Mollie charge; inaczej PARK Purchase z notatką.
8. Screenshot + update `L0-INSTRUMENTATION.md` + handoff evidence.

## Zakazy

- Agent nie klika Ads Manager create/publish kampanii €.
- Agent nie obchodzi 2FA / nie prosi o hasło w czacie.
- Fake PASS zabroniony.
