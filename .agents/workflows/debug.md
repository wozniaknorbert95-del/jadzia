---
description: 5-krokowa diagnostyka z dowodem — jadzia-core FastAPI/service.
---

# /debug

## KROK 1 — ZBIERZ DANE

Error, timing, determinism, environment (local/VPS), endpoint or Telegram command.

## KROK 2 — LOGI

Local: pytest output, uvicorn stderr.  
VPS (Commander runs): `journalctl -u jadzia -n 100`, `tail -50 /root/jadzia/logs/jadzia-error.log` per [vps-ops.md](https://github.com/wozniaknorbert95-del/bouwplaats-chaos/blob/main/docs/core/vps-ops.md).

## KROK 3 — IZOLUJ

Python module, LangGraph node, DB lock, webhook payload, SSH executor scope.

## KROK 4 — ROOT CAUSE

Jedno zdanie + dowód (log line, stack trace, failing test).

## KROK 5 — PROPOZYCJA

Konkretna zmiana + verification plan (`pytest`, `/health`).

Czekaj na potwierdzenie Dowódcy.

## Output

```text
ISSUE: [...]
REPRO: [...]
ROOT_CAUSE: [...]
PROPOSED_FIX: [...]
VERIFICATION: [...]

---
CURRENT_STAGE: F4-Test
RECOMMENDED_NEXT: [/implement | /jadzia-test | /audit-red-team | /context-reset]
WHY_NEXT: [...]
---
```
