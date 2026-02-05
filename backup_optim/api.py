"""
api.py — FastAPI endpoints dla JADZIA
"""

# ============================================================
# DODANE: wczytanie pliku .env
# ============================================================
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional, List
import asyncio

from agent.agent import process_message
from agent.state import load_state, clear_state, force_unlock
from agent.tools import rollback, health_check, test_ssh_connection
from agent.log import get_recent_logs

# ============================================================
# APP
# ============================================================

app = FastAPI(
    title="JADZIA API",
    description="AI Agent do zarzadzania sklepem internetowym",
    version="1.0.0"
)


# ============================================================
# MODELE
# ============================================================

class ChatRequest(BaseModel):
    message: str
    chat_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    awaiting_input: bool
    input_type: Optional[str] = None


class StatusResponse(BaseModel):
    status: str
    operation: Optional[dict] = None


class RollbackResponse(BaseModel):
    status: str
    restored: List[str] = []
    errors: List[str] = []
    message: str


# ============================================================
# ENDPOINTS
# ============================================================

@app.get("/")
async def root():
    """Health check endpoint"""
    return {
        "status": "ok",
        "agent": "JADZIA",
        "version": "1.0.0",
        "message": "Agent gotowy do pracy"
    }


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    Główny endpoint do komunikacji z agentem.
    
    Używany przez n8n do przekazywania wiadomości z Telegram.
    """
    try:
        response, awaiting_input, input_type = await process_message(
            user_input=request.message,
            chat_id=request.chat_id
        )
        
        return ChatResponse(
            response=response,
            awaiting_input=awaiting_input,
            input_type=input_type
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status", response_model=StatusResponse)
async def status():
    """
    Zwraca aktualny status agenta i operacji.
    """
    state = load_state()
    
    if not state:
        return StatusResponse(status="idle", operation=None)
    
    return StatusResponse(
        status=state.get("status", "unknown"),
        operation={
            "id": state.get("id"),
            "user_input": state.get("user_input", "")[:100],
            "created_at": state.get("created_at"),
            "files_to_modify": state.get("files_to_modify", []),
            "files_written": state.get("files_written", []),
            "awaiting_response": state.get("awaiting_response", False)
        }
    )


@app.post("/rollback", response_model=RollbackResponse)
async def do_rollback():
    """
    Wykonuje rollback ostatnich zmian.
    """
    try:
        result = rollback()
        clear_state()
        
        return RollbackResponse(
            status=result.get("status", "error"),
            restored=result.get("restored", []),
            errors=result.get("errors", []),
            message=result.get("msg", "Rollback wykonany")
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/health")
async def health():
    """
    Sprawdza health sklepu.
    """
    result = health_check()
    return result


@app.get("/logs")
async def logs(limit: int = 20):
    """
    Zwraca ostatnie logi.
    """
    return {"logs": get_recent_logs(limit=limit)}


@app.post("/clear")
async def clear():
    """
    Czyści aktualny stan (awaryjne).
    """
    force_unlock()
    clear_state()
    return {"status": "ok", "message": "Stan wyczyszczony"}


@app.get("/test-ssh")
async def test_ssh():
    """
    Testuje połączenie SSH.
    """
    success, message = test_ssh_connection()
    return {
        "status": "ok" if success else "error",
        "message": message
    }


# ============================================================
# STARTUP
# ============================================================

@app.on_event("startup")
async def startup():
    """Inicjalizacja przy starcie"""
    from pathlib import Path
    Path("data").mkdir(exist_ok=True)
    print("=" * 50)
    print("  JADZIA API uruchomiona")
    print("  Endpoints: /chat, /status, /rollback, /health")
    print("=" * 50)


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
