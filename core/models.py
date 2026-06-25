"""Pydantic models for request/response schemas and domain objects."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


# ──────────────────────────────────────────────
# Chat / Agent models
# ──────────────────────────────────────────────

class ChatRequest(BaseModel):
    message: str
    chat_id: str = "default"


class ChatResponse(BaseModel):
    response: str
    awaiting_input: bool
    input_type: Optional[str] = None


class CustomerChatRequest(BaseModel):
    session_id: str
    message: str


class CustomerChatResponse(BaseModel):
    reply: str
    lead: dict = Field(default_factory=dict)
    lead_score: Optional[int] = None
    intent: Optional[str] = None
    category: Optional[str] = None
    reason: Optional[str] = None


class PortalQualifyUiSuggestion(BaseModel):
    value: str
    label_nl: str


class PortalQualifyCta(BaseModel):
    type: str
    label_nl: str
    url: str


class PortalQualifyRequest(BaseModel):
    session_id: str
    message: str = ""
    step: Optional[str] = None
    consent_lead_storage: bool = False


class PortalQualifyResponse(BaseModel):
    schema_version: str = "qual_v1"
    reply: str
    step_next: str
    ui_suggestions: List[PortalQualifyUiSuggestion] = Field(default_factory=list)
    qualification_profile: Dict[str, Optional[str]] = Field(default_factory=dict)
    recommended_preset_id: Optional[str] = None
    wizard_deep_link: Optional[str] = None
    cta: Optional[PortalQualifyCta] = None
    lead_saved: bool = False


class StatusResponse(BaseModel):
    status: str
    operation: Optional[dict] = None


class RollbackResponse(BaseModel):
    status: str
    restored: List[str] = []
    errors: List[str] = []
    message: str


# ──────────────────────────────────────────────
# Worker Task API models
# ──────────────────────────────────────────────

class WorkerTaskRequest(BaseModel):
    instruction: str
    chat_id: str
    webhook_url: Optional[str] = None
    test_mode: bool = False


class WorkerTaskCreateResponse(BaseModel):
    task_id: str
    status: str
    position_in_queue: int
    chat_id: Optional[str] = None
    dry_run: bool = False
    test_mode: bool = False


class WorkerTaskInputRequest(BaseModel):
    approval: Optional[bool] = None
    answer: Optional[str] = None


class WorkerTasksCleanupRequest(BaseModel):
    task_ids: List[str]
    reason: Optional[str] = None


class WorkerTasksCleanupResponse(BaseModel):
    updated: List[str]
    skipped_terminal: List[str]
    not_found: List[str]


class WorkerTaskOperation(BaseModel):
    id: Optional[str] = None
    plan: Optional[Any] = None
    diffs: Optional[Dict[str, str]] = None
    user_input: Optional[str] = None
    files_to_modify: Optional[List[str]] = None
    created_at: Optional[str] = None
    awaiting_response: bool = False


class WorkerTaskResponse(BaseModel):
    task_id: str
    status: str
    position_in_queue: int = 0
    awaiting_input: bool = False
    input_type: Optional[str] = None
    response: Optional[str] = None
    operation: Optional[WorkerTaskOperation] = None
    dry_run: bool = False
    test_mode: bool = False


# ──────────────────────────────────────────────
# Telegram models
# ──────────────────────────────────────────────

class TelegramUser(BaseModel):
    id: int
    is_bot: bool = False
    first_name: str = ""
    last_name: Optional[str] = None
    username: Optional[str] = None
    language_code: Optional[str] = None


class TelegramChat(BaseModel):
    id: int
    type: str = "private"
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    username: Optional[str] = None


class TelegramMessage(BaseModel):
    message_id: int
    from_user: Optional[TelegramUser] = Field(None, alias="from")
    chat: TelegramChat
    text: Optional[str] = None
    date: int

    model_config = ConfigDict(populate_by_name=True)


class CallbackQuery(BaseModel):
    id: str
    from_user: TelegramUser = Field(alias="from")
    message: Optional[TelegramMessage] = None
    data: Optional[str] = None

    model_config = ConfigDict(populate_by_name=True)


class TelegramUpdate(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    callback_query: Optional[CallbackQuery] = None


class TelegramWebhookRequest(BaseModel):
    update_id: int
    message: Optional[TelegramMessage] = None
    callback_query: Optional[CallbackQuery] = None


# ──────────────────────────────────────────────
# Health / Metrics models
# ──────────────────────────────────────────────

class DeploymentVerification(BaseModel):
    timestamp: Optional[str] = None
    healthy: Optional[bool] = None
    auto_rollback_count: int = 0


class HealthMetrics(BaseModel):
    startup_time: Optional[str] = None
    last_success: Optional[str] = None
    total_tasks: int = 0
    failed_tasks: int = 0
    errors_last_hour: List[dict] = []
    last_deployment_verification: DeploymentVerification = Field(default_factory=DeploymentVerification)


class WorkerHealthResponse(BaseModel):
    status: str
    uptime_seconds: int = 0
    worker_loop_alive: bool = False
    active_sessions: int = 0
    active_tasks: int = 0
    queue_length: int = 0
    total_tasks: int = 0
    ssh_connection: str = "unknown"
    sqlite_connection: bool = False
    last_success: Optional[str] = None
    errors_last_hour: int = 0
    failed_tasks_total: int = 0
    last_deployment_verification: Optional[DeploymentVerification] = None


# ──────────────────────────────────────────────
# Dashboard models
# ──────────────────────────────────────────────

class DashboardMetrics(BaseModel):
    total_tasks: int = 0
    by_status: Dict[str, int] = {}
    test_mode_tasks: int = 0
    production_tasks: int = 0
    recent_tasks: List[dict] = []
    errors_last_24h: int = 0
    avg_duration_seconds: Optional[float] = None


class TaskListItem(BaseModel):
    task_id: str
    status: str
    test_mode: bool = False
    dry_run: bool = False
    created_at: str = ""
    duration_seconds: float = 0.0


# ──────────────────────────────────────────────
# Agent / Operation models
# ──────────────────────────────────────────────

class OperationState(BaseModel):
    id: Optional[str] = None
    operation_id: Optional[str] = None
    status: str = "planning"
    user_input: str = ""
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    plan: Optional[Any] = None
    files_to_modify: List[str] = []
    diffs: Dict[str, str] = {}
    new_contents: Dict[str, str] = {}
    written_files: Dict[str, Any] = {}
    errors: List[Dict[str, str]] = []
    awaiting_response: bool = False
    awaiting_type: Optional[str] = None
    dry_run: bool = False
    test_mode: bool = False
    webhook_url: Optional[str] = None
    last_response: Optional[str] = None


class SessionState(BaseModel):
    chat_id: str = "default"
    source: str = "http"
    tasks: Dict[str, OperationState] = {}
    active_task_id: Optional[str] = None
    task_queue: List[str] = []


# ──────────────────────────────────────────────
# Cost tracking models
# ──────────────────────────────────────────────

class CostStats(BaseModel):
    input_tokens: int = 0
    output_tokens: int = 0
    cached_tokens: int = 0
    total_cost: float = 0.0
    model: str = ""


class CostEstimateRequest(BaseModel):
    message: str
    task_complexity: str = "auto"


class CostEstimateResponse(BaseModel):
    estimated_input_tokens: int = 0
    estimated_output_tokens: int = 0
    estimated_cost: float = 0.0
    model: str = ""
