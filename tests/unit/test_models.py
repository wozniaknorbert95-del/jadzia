"""Unit tests for core/models.py — Pydantic model validation."""

import pytest
from pydantic import ValidationError

from core.models import (
    ChatRequest,
    ChatResponse,
    CustomerChatRequest,
    CustomerChatResponse,
    StatusResponse,
    RollbackResponse,
    WorkerTaskRequest,
    WorkerTaskCreateResponse,
    WorkerTaskInputRequest,
    WorkerTasksCleanupRequest,
    WorkerTasksCleanupResponse,
    WorkerTaskResponse,
    WorkerTaskOperation,
    TelegramUpdate,
    TelegramMessage,
    TelegramUser,
    TelegramChat,
    HealthMetrics,
    DeploymentVerification,
    WorkerHealthResponse,
    DashboardMetrics,
    TaskListItem,
    OperationState,
    SessionState,
    CostStats,
    CostEstimateRequest,
    CostEstimateResponse,
)


class TestChatModels:
    def test_chat_request_defaults(self):
        r = ChatRequest(message="hello")
        assert r.message == "hello"
        assert r.chat_id == "default"

    def test_chat_request_custom_chat_id(self):
        r = ChatRequest(message="test", chat_id="custom_123")
        assert r.chat_id == "custom_123"

    def test_chat_request_empty_message(self):
        with pytest.raises(ValidationError):
            ChatRequest()

    def test_chat_response_required_fields(self):
        r = ChatResponse(response="ok", awaiting_input=False)
        assert r.response == "ok"
        assert r.awaiting_input is False
        assert r.input_type is None

    def test_chat_response_with_input_type(self):
        r = ChatResponse(response="confirm?", awaiting_input=True, input_type="approval")
        assert r.input_type == "approval"


class TestCustomerChatModels:
    def test_customer_chat_request(self):
        r = CustomerChatRequest(session_id="sess_1", message="hi")
        assert r.session_id == "sess_1"
        assert r.message == "hi"

    def test_customer_chat_response(self):
        r = CustomerChatResponse(reply="hello!", lead={"score": 0.8})
        assert r.reply == "hello!"
        assert r.lead["score"] == 0.8
        assert r.lead_score is None
        assert r.intent is None

    def test_customer_chat_response_with_lead_scoring(self):
        r = CustomerChatResponse(
            reply="Oto wycena",
            lead={"score": 80, "intent": "high"},
            lead_score=80,
            intent="high",
            category="wycena",
            reason="Wykryto wysoki potencjał zakupowy",
        )
        assert r.lead_score == 80
        assert r.intent == "high"
        assert r.category == "wycena"
        assert r.reason is not None


class TestStatusRollbackModels:
    def test_status_response_idle(self):
        r = StatusResponse(status="idle")
        assert r.status == "idle"
        assert r.operation is None

    def test_status_response_with_operation(self):
        r = StatusResponse(status="planning", operation={"id": "op_123"})
        assert r.operation["id"] == "op_123"

    def test_rollback_response_defaults(self):
        r = RollbackResponse(status="ok", message="done")
        assert r.restored == []
        assert r.errors == []

    def test_rollback_response_with_data(self):
        r = RollbackResponse(
            status="ok",
            restored=["file1.php"],
            errors=[],
            message="rolled back",
        )
        assert r.restored == ["file1.php"]


class TestWorkerTaskModels:
    def test_worker_task_request(self):
        r = WorkerTaskRequest(instruction="update site", chat_id="chat_1")
        assert r.instruction == "update site"
        assert r.test_mode is False

    def test_worker_task_create_response(self):
        r = WorkerTaskCreateResponse(
            task_id="task_1",
            status="queued",
            position_in_queue=0,
        )
        assert r.task_id == "task_1"
        assert r.dry_run is False

    def test_worker_task_input_approval(self):
        r = WorkerTaskInputRequest(approval=True)
        assert r.approval is True
        assert r.answer is None

    def test_worker_task_input_answer(self):
        r = WorkerTaskInputRequest(answer="some text")
        assert r.approval is None
        assert r.answer == "some text"

    def test_worker_task_input_both_none(self):
        r = WorkerTaskInputRequest()
        assert r.approval is None
        assert r.answer is None

    def test_cleanup_request(self):
        r = WorkerTasksCleanupRequest(task_ids=["t1", "t2"], reason="stuck")
        assert r.task_ids == ["t1", "t2"]
        assert r.reason == "stuck"

    def test_cleanup_response(self):
        r = WorkerTasksCleanupResponse(
            updated=["t1"],
            skipped_terminal=[],
            not_found=["t2"],
        )
        assert r.updated == ["t1"]
        assert r.not_found == ["t2"]

    def test_worker_task_response(self):
        r = WorkerTaskResponse(
            task_id="t1",
            status="in_progress",
        )
        assert r.task_id == "t1"
        assert r.position_in_queue == 0

    def test_worker_task_operation(self):
        op = WorkerTaskOperation(
            id="op_1",
            user_input="fix colors",
            files_to_modify=["style.css"],
        )
        assert op.id == "op_1"
        assert op.files_to_modify == ["style.css"]


class TestTelegramModels:
    def test_telegram_user(self):
        u = TelegramUser(id=12345, is_bot=False, first_name="Test")
        assert u.id == 12345
        assert u.username is None

    def test_telegram_chat(self):
        c = TelegramChat(id=67890, type="private")
        assert c.id == 67890

    def test_telegram_message(self):
        msg = TelegramMessage(
            message_id=1,
            from_user={"id": 123, "first_name": "User"},
            chat={"id": 456, "type": "private"},
            text="hello",
            date=1700000000,
        )
        assert msg.message_id == 1
        assert msg.text == "hello"

    def test_telegram_update_with_message(self):
        update = TelegramUpdate(
            update_id=100,
            message={
                "message_id": 1,
                "from": {"id": 123, "first_name": "User"},
                "chat": {"id": 456, "type": "private"},
                "text": "hello",
                "date": 1700000000,
            },
        )
        assert update.update_id == 100
        assert update.message is not None
        assert update.callback_query is None


class TestHealthMetricsModels:
    def test_deployment_verification_defaults(self):
        dv = DeploymentVerification()
        assert dv.auto_rollback_count == 0
        assert dv.timestamp is None

    def test_health_metrics(self):
        hm = HealthMetrics(total_tasks=10, failed_tasks=2)
        assert hm.total_tasks == 10
        assert hm.failed_tasks == 2

    def test_worker_health_response_defaults(self):
        whr = WorkerHealthResponse(status="healthy")
        assert whr.status == "healthy"
        assert whr.uptime_seconds == 0


class TestDashboardModels:
    def test_dashboard_metrics_defaults(self):
        dm = DashboardMetrics()
        assert dm.total_tasks == 0
        assert dm.by_status == {}

    def test_task_list_item(self):
        tli = TaskListItem(task_id="t1", status="completed")
        assert tli.task_id == "t1"
        assert tli.dry_run is False


class TestOperationStateModels:
    def test_operation_state_defaults(self):
        op = OperationState(user_input="test")
        assert op.status == "planning"
        assert op.files_to_modify == []

    def test_session_state(self):
        ss = SessionState(chat_id="chat_1", source="telegram")
        assert ss.chat_id == "chat_1"
        assert ss.tasks == {}


class TestCostModels:
    def test_cost_stats(self):
        cs = CostStats(input_tokens=100, output_tokens=50, total_cost=0.001)
        assert cs.input_tokens == 100
        assert cs.total_cost == 0.001

    def test_cost_estimate_request(self):
        r = CostEstimateRequest(message="hello world")
        assert r.message == "hello world"
        assert r.task_complexity == "auto"

    def test_cost_estimate_response(self):
        r = CostEstimateResponse(
            estimated_input_tokens=10,
            estimated_output_tokens=5,
            estimated_cost=0.0001,
            model="haiku",
        )
        assert r.model == "haiku"
