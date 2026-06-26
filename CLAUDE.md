# JADZIA — Chief Operating Intelligence (COI) backend

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in your values
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Architecture

See `brain.md` and `docs/PRD-core.md` for the complete reference.
Module spec: `flexgrafik-meta/docs/core/modules/module-jadzia-core.md`

**WP agent flow:** User -> Telegram -> `api/telegram.py` -> Worker Queue (SQLite) -> `api/app.py` worker_loop -> `core/agent.py` -> SSH Orchestrator -> response

**Widget flow:** Wizard -> `POST /api/v1/widget/chat` -> `agent/customer_agent.py` -> Claude (INT-001)

**Key files:**
- `api/app.py` - FastAPI app factory + worker loop
- `api/telegram.py` - Telegram webhook handler
- `core/agent.py` - Orchestration (`process_message`)
- `core/llm.py` - Claude API client
- `agent/state/` - Session state (SQLite-backed)
- `agent/db.py` - SQLite database layer
- `agent/tools/ssh_orchestrator.py` - SSH file operations

## Rules

- **SQLite is the single source of truth** for task_id, session state
- **No in-memory dicts** for task state (use DB)
- **Backup before write** on SSH operations
- **Every log must have context**: task_id, chat_id
- **Use logger, not print()** for all logging
- **%-style formatting** for logger calls: `logger.info("msg %s", var)`

## Testing

```bash
pytest tests/
```

## Environment

Required: `ANTHROPIC_API_KEY`, `JWT_SECRET`, `SSH_HOST`, `SSH_USER`, `SSH_PASSWORD`, `BASE_PATH`, `TELEGRAM_BOT_TOKEN`

See `.env.example` for full list.
