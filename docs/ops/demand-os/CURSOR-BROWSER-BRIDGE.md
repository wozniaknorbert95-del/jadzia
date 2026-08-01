---
status: "[ACTIVE · BRIDGE]"
title: "Cursor Browser ↔ Agent control — jak to działa"
updated: "2026-08-01"
---

# Cursor Browser Bridge

## Prawda techniczna

| Przeglądarka | Agent może sterować? |
|--------------|----------------------|
| **Cursor Simple Browser** (zakładka w IDE, WebView2) — tu jesteś zalogowany na TT | **NIE przez chrome-devtools MCP** — brak CDP |
| **Chrome z `--remote-debugging-port=9222`** + Twój profil Default | **TAK** — to most agenta |

## Co naprawione

1. `~/.cursor/mcp.json` — chrome-devtools → `127.0.0.1:9222` + user data dir Chrome  
2. `tools/ensure_chrome_cdp.ps1` — trzyma CDP przy życiu  
3. Settings: `cursor.browserAutomation.enabled` + preferredBrowser `browserTab`

## Co musisz zrobić RAZ (Cursor UI)

1. **Cursor Settings → Tools & MCP → Browser Automation → Browser Tab** (nie Off)  
2. **Wyłącz konflikt:** jeśli Browser Tab dalej nie daje narzędzi agentowi, trzymaj chrome-devtools jak jest (most CDP)  
3. **Nowa sesja agenta** po zmianie MCP (reload MCP / restart Cursor)  
4. Na Chrome CDP (okno systemowe): **zaloguj TikTok QR lub Google** (sesja WebView ≠ sesja Chrome)

## Publish flow (agent)

```text
powershell -File tools/ensure_chrome_cdp.ps1
→ agent: list_pages / navigate Studio upload
→ upload video + caption
→ LEDGER publish=Y
```

## STOP

Nie zabijać procesu Cursor. Nie oczekiwać, że WebView „magicznie” wejdzie w MCP bez Browser Tab / CDP.
