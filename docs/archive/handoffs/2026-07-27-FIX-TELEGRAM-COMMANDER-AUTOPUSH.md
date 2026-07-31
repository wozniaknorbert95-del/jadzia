---
status: "[CLOSED]"
title: "FIX Telegram /commander + autopush mute"
updated: "2026-07-27"
gate: "FIX-TELEGRAM-COMMANDER-AUTOPUSH"
prod_tip: "de10e83"
commit: "de10e83"
deploy: true
---

# FIX — Telegram `/commander` + autopush

## Done

1. `/commander` reply = **plain text** + inline button **Otwórz Commander** (no MarkdownV2 on URL).
2. `TELEGRAM_AUTOPUSH_ENABLED=0` on VPS — gates alerts, MB proposals/eval/scorecard, brain_bus TG, SLA escalation TG.
3. Command replies (`/commander`, `/status`, …) **not** gated.

## Deploy

| Step | Result |
|------|--------|
| Commit | `de10e83` |
| VPS tip | `de10e83` TIP_MATCH=OK |
| Backup | `jadzia-pre-tg-fix-20260727-203416.db` |
| Env | `TELEGRAM_AUTOPUSH_ENABLED=0` |
| Health | OK |

## Verify (Founder)

Telegram → `/commander` → plain link + button **Otwórz Commander** → HQ zalogowany.

## Residuals

- Mail + full notification map → HQ (later)
- Re-enable autopush: VPS `TELEGRAM_AUTOPUSH_ENABLED=1` + restart
