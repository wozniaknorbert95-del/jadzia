---
status: "[CLOSED]"
title: "FIX Telegram /commander + autopush mute"
updated: "2026-07-27"
gate: "FIX-TELEGRAM-COMMANDER-AUTOPUSH"
commit: pending
---

# FIX — Telegram `/commander` + autopush

## Done

1. `/commander` reply = **plain text** + inline button **Otwórz Commander** (no MarkdownV2 on URL).
2. `TELEGRAM_AUTOPUSH_ENABLED` default **OFF** — gates alerts, MB proposals/eval/scorecard, brain_bus TG, SLA escalation TG.
3. Command replies (`/commander`, `/status`, …) **not** gated.

## Verify

- Unit: `test_commander_session_login` + `test_telegram_autopush` PASS
- Prod dogfood: Telegram `/commander` → klikalny link/button → HQ login

## Residuals

- Mail + full notification map → HQ (later)
- Re-enable autopush: VPS `TELEGRAM_AUTOPUSH_ENABLED=1` + restart
