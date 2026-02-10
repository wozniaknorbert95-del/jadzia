# JADZIA - AI Agent do zarządzania sklepem internetowym

## Quick Start

```bash
pip install -r requirements.txt
cp .env.example .env  # fill in your values
uvicorn main:app --host 0.0.0.0 --port 8000
```

## Architecture

See `SYSTEM_BIBLE.md` for the complete architecture reference.

**Flow:** User -> Telegram -> telegram_api.py -> Worker Queue (SQLite) -> worker_loop (api.py) -> process_message (agent.py) -> SSH Orchestrator -> Telegram response

**Key files:**
- `interfaces/api.py` - FastAPI app + worker loop
- `interfaces/telegram_api.py` - Telegram webhook handler
- `agent/agent.py` - Core AI agent logic
- `agent/state.py` - Session state management
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
