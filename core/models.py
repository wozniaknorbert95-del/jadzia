"""Pydantic models for request/response schemas and domain objects."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

import re

from pydantic import BaseModel, ConfigDict, Field, field_validator


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


class WooOrderItem(BaseModel):
    sku: str
    qty: int = Field(ge=1)
    price: float = Field(ge=0)


class WooOrderCustomer(BaseModel):
    email: str
    name: str = ""


class WooOrderWebhookRequest(BaseModel):
    """INT-002 inbound payload from zzpackage WooCommerce."""

    order_id: str = Field(min_length=1)
    status: Literal["processing", "completed"]
    items: List[WooOrderItem] = Field(min_length=1)
    customer: WooOrderCustomer
    total_gross: float = Field(ge=0)
    payment_id: str = ""

    @field_validator("order_id", "payment_id", mode="before")
    @classmethod
    def _strip_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class WooOrderWebhookResponse(BaseModel):
    """INT-002 response contract."""

    db_status: Literal["success", "fail"]
    order_internal_id: str = ""


class LeadCreateRequest(BaseModel):
    """INT-004 inbound payload from app.flexgrafik.nl."""

    email: str = Field(min_length=3)
    name: str = ""
    source: Literal["game", "web"] = "game"
    consent_status: bool
    game_score: Optional[int] = Field(default=None, ge=0)
    reward_tier: Optional[str] = None

    @field_validator("email")
    @classmethod
    def _validate_email(cls, v: str) -> str:
        v = v.strip().lower()
        if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", v):
            raise ValueError("invalid email format")
        return v

    @field_validator("name", "reward_tier", mode="before")
    @classmethod
    def _strip_optional_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class LeadCreateResponse(BaseModel):
    """INT-004 / lead_node output."""

    lead_id: str = ""
    sync_status: Literal["success", "duplicate", "fail"]


class AnalyticsSourceAppMetrics(BaseModel):
    """INT-009 app.flexgrafik.nl GA4 metrics."""

    active_users: int = 0
    sessions: int = 0
    avg_session_duration_sec: float = 0.0
    game_starts: int = 0
    lead_captured: int = 0
    dau_1d: Optional[int] = None


class AnalyticsSourceZzpackageMetrics(BaseModel):
    """INT-009 zzpackage Wizard GA4 metrics."""

    sessions: int = 0
    conversions: int = 0
    purchase_revenue: float = 0.0
    aov: float = 0.0


class AnalyticsSnapshotSources(BaseModel):
    """Per-source metrics bundle."""

    app: Optional[AnalyticsSourceAppMetrics] = None
    zzpackage: Optional[AnalyticsSourceZzpackageMetrics] = None


class AnalyticsSnapshotResponse(BaseModel):
    """INT-009 / analytics_node output."""

    sync_status: Literal["success", "degraded", "fail"]
    generated_at: str
    period: str
    sources: AnalyticsSnapshotSources = Field(default_factory=AnalyticsSnapshotSources)
    errors: List[str] = Field(default_factory=list)


class ContentCalendarCreateRequest(BaseModel):
    """INT-010 inbound — create calendar entry."""

    platform: Literal["facebook", "tiktok"]
    title: str = Field(min_length=1, max_length=200)
    body_nl: str = Field(min_length=1, max_length=5000)
    scheduled_at: str
    source_order_id: Optional[str] = None

    @field_validator("title", "body_nl", mode="before")
    @classmethod
    def _strip_strings(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class ContentCalendarUpdateRequest(BaseModel):
    """INT-010 partial update."""

    title: Optional[str] = Field(default=None, min_length=1, max_length=200)
    body_nl: Optional[str] = Field(default=None, min_length=1, max_length=5000)
    scheduled_at: Optional[str] = None
    status: Optional[Literal["draft", "pending_approval", "approved", "published", "cancelled"]] = None

    @field_validator("title", "body_nl", mode="before")
    @classmethod
    def _strip_optional(cls, v: object) -> object:
        if isinstance(v, str):
            return v.strip()
        return v


class ContentCalendarEntry(BaseModel):
    """INT-010 calendar row."""

    entry_id: str
    platform: Literal["facebook", "tiktok"]
    title: str
    body_nl: str
    scheduled_at: str
    status: Literal["draft", "pending_approval", "approved", "published", "cancelled"]
    source_order_id: Optional[str] = None
    created_at: str
    updated_at: str


class ContentCalendarListResponse(BaseModel):
    """INT-010 list response."""

    entries: List[ContentCalendarEntry] = Field(default_factory=list)
    total: int = 0


class ContentCalendarCreateResponse(BaseModel):
    """INT-010 / content_calendar_node create output."""

    entry_id: str
    sync_status: Literal["success", "fail"]


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
