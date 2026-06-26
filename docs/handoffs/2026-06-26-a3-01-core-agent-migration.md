## Handoff: A3-01 — Agent migration to core/

**Data:** 2026-06-26
**Autor:** Agent

### Co zrobiono

- Utworzono [`core/llm.py`](core/llm.py): `call_claude`, `call_claude_with_retry`, `detect_session_source`, `get_cost_stats`, modele
- [`core/agent.py`](core/agent.py): importy z `core.llm` (bez lazy import z legacy)
- [`agent/agent.py`](agent/agent.py): cienki shim re-exportujący `core.agent` + `core.llm`
- Testy CI: patch `core.agent.call_claude_with_retry`

### Testy

**304 passed**, 1 skipped, 1 xfailed

### Następny krok

A5-01 (CLI) lub D1-03 (EN comments). S1-01 rotacja sekretów — Dowódca.
