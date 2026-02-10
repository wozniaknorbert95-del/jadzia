"""
Tests for Phase 1: Security Hardening.

Covers:
- Command injection prevention in ssh_orchestrator.list_files()
- Path traversal prevention in guardrails.get_safe_path()
- Hardcoded credential removal in wp_explorer config
- JWT auth-disabled warning
- Approval double-submit idempotency guard
"""

import os
import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock, AsyncMock

from agent.guardrails import get_safe_path


# ================================================================
# 1. get_safe_path — Path Traversal Prevention
# ================================================================


class TestGetSafePath:
    """Verify get_safe_path blocks all forms of directory traversal."""

    BASE = "/home/user/public_html"

    def test_simple_relative_path(self):
        result = get_safe_path(self.BASE, "style.css")
        assert result.startswith(str(Path(self.BASE).resolve()))
        assert result.endswith("style.css")

    def test_nested_relative_path(self):
        result = get_safe_path(self.BASE, "wp-content/themes/child/style.css")
        assert result.startswith(str(Path(self.BASE).resolve()))
        assert "wp-content/themes/child/style.css" in result

    def test_empty_relative_path(self):
        result = get_safe_path(self.BASE, "")
        assert result == self.BASE.rstrip("/")

    def test_leading_slash_stripped(self):
        result = get_safe_path(self.BASE, "/style.css")
        assert result.startswith(str(Path(self.BASE).resolve()))
        assert result.endswith("style.css")

    def test_basic_traversal_blocked(self):
        with pytest.raises(PermissionError, match="traversal"):
            get_safe_path(self.BASE, "../../../etc/passwd")

    def test_double_dot_in_middle_blocked(self):
        with pytest.raises(PermissionError, match="traversal"):
            get_safe_path(self.BASE, "wp-content/../../etc/passwd")

    def test_deep_traversal_blocked(self):
        """Deep traversal with many ../ levels should be blocked."""
        with pytest.raises(PermissionError, match="traversal"):
            get_safe_path(self.BASE, "a/b/c/../../../../../../../../etc/passwd")

    def test_backslash_traversal_blocked(self):
        with pytest.raises(PermissionError, match="traversal"):
            get_safe_path(self.BASE, "..\\..\\etc\\passwd")

    def test_mixed_separator_traversal_blocked(self):
        with pytest.raises(PermissionError, match="traversal"):
            get_safe_path(self.BASE, "wp-content\\..\\..\\etc\\passwd")

    def test_absolute_path_injection_resolved_under_base(self):
        """Absolute path like /etc/passwd should resolve under base (leading / is stripped)."""
        result = get_safe_path(self.BASE, "/etc/passwd")
        # After stripping leading /, it should resolve under BASE as "etc/passwd"
        assert result.startswith(str(Path(self.BASE).resolve()))

    def test_result_is_resolved(self):
        """Result should be a canonical path (no ./ or ../ components)."""
        result = get_safe_path(self.BASE, "./wp-content/./themes/../themes/style.css")
        assert ".." not in result
        # Should contain the cleaned path
        assert "wp-content/themes/style.css" in result

    def test_traversal_with_inner_dotdot(self):
        """Traversal with ../ that cancels out but ultimately escapes."""
        with pytest.raises(PermissionError, match="traversal"):
            get_safe_path(self.BASE, "a/../../../etc/shadow")


# ================================================================
# 2. list_files — Command Injection Prevention
# ================================================================


class TestListFilesInjection:
    """Verify list_files rejects malicious patterns and shell-quotes args."""

    def test_safe_pattern_accepted(self):
        """Normal glob patterns should pass the regex."""
        from agent.tools.ssh_orchestrator import _SAFE_GLOB_RE
        assert _SAFE_GLOB_RE.match("*.php")
        assert _SAFE_GLOB_RE.match("*.css")
        assert _SAFE_GLOB_RE.match("style[0-9].css")
        assert _SAFE_GLOB_RE.match("inc/*.php")

    def test_injection_semicolon_rejected(self):
        from agent.tools.ssh_orchestrator import _SAFE_GLOB_RE
        assert not _SAFE_GLOB_RE.match("'; rm -rf /; echo '")

    def test_injection_backtick_rejected(self):
        from agent.tools.ssh_orchestrator import _SAFE_GLOB_RE
        assert not _SAFE_GLOB_RE.match("`whoami`")

    def test_injection_dollar_rejected(self):
        from agent.tools.ssh_orchestrator import _SAFE_GLOB_RE
        assert not _SAFE_GLOB_RE.match("$(cat /etc/passwd)")

    def test_injection_pipe_rejected(self):
        from agent.tools.ssh_orchestrator import _SAFE_GLOB_RE
        assert not _SAFE_GLOB_RE.match("*.php | cat /etc/passwd")

    def test_injection_ampersand_rejected(self):
        from agent.tools.ssh_orchestrator import _SAFE_GLOB_RE
        assert not _SAFE_GLOB_RE.match("*.php && cat /etc/passwd")

    def test_list_files_raises_on_unsafe_pattern(self):
        """list_files should raise ValueError for unsafe patterns."""
        from agent.tools import ssh_orchestrator

        with patch.object(ssh_orchestrator, "exec_command_ssh") as mock_exec:
            with pytest.raises(ValueError, match="Unsafe file pattern"):
                ssh_orchestrator.list_files(pattern="'; rm -rf /; echo '")
            mock_exec.assert_not_called()

    def test_list_files_directory_traversal_blocked(self):
        """list_files should block directory traversal in the directory parameter."""
        from agent.tools import ssh_orchestrator

        with patch.object(ssh_orchestrator, "exec_command_ssh") as mock_exec:
            with pytest.raises(PermissionError):
                ssh_orchestrator.list_files(pattern="*.php", directory="../../etc")
            mock_exec.assert_not_called()

    def test_list_files_safe_pattern_uses_shlex_quote(self):
        """list_files should shell-quote the pattern in the find command."""
        from agent.tools import ssh_orchestrator
        import shlex

        with patch.object(ssh_orchestrator, "exec_command_ssh") as mock_exec:
            mock_exec.return_value = (True, "", "")
            ssh_orchestrator.list_files(pattern="*.php")

            cmd = mock_exec.call_args[0][4]  # 5th positional arg is the command
            assert shlex.quote("*.php") in cmd


# ================================================================
# 3. Hardcoded Credentials Removal
# ================================================================


class TestNoHardcodedCredentials:
    """Verify no production credentials are committed as fallback defaults."""

    def test_no_production_hostname_in_source(self):
        """Scan the config source file for known production hostnames."""
        config_path = Path(__file__).parent.parent / "agent" / "tools" / "wp_explorer" / "config.py"
        content = config_path.read_text()
        assert "s34.cyber-folks.pl" not in content, "Production hostname still hardcoded"
        assert "uhqsycwpjz" not in content, "Production username still hardcoded"

    def test_no_hardcoded_shop_url(self):
        """shop_url should come from env, not be hardcoded."""
        config_path = Path(__file__).parent.parent / "agent" / "tools" / "wp_explorer" / "config.py"
        content = config_path.read_text()
        assert "zzpackage.flexgrafik" not in content, "Production shop URL still hardcoded"

    def test_default_port_is_standard(self):
        """Default SSH port should be standard 22, not a custom production port."""
        config_path = Path(__file__).parent.parent / "agent" / "tools" / "wp_explorer" / "config.py"
        content = config_path.read_text()
        # The old default was "222" which was production-specific
        assert 'or "222"' not in content, "Production SSH port 222 still hardcoded"


# ================================================================
# 4. JWT Auth Warning
# ================================================================


class TestJWTAuthWarning:
    """Verify JWT auth logs a warning when secret is not set."""

    @pytest.mark.asyncio
    async def test_jwt_disabled_warning_logged(self, capsys):
        """When JWT_SECRET is None, verify_worker_jwt should log a security warning."""
        import interfaces.api as api_mod

        api_mod._jwt_warning_logged = False
        original_secret = api_mod.JWT_SECRET
        try:
            api_mod.JWT_SECRET = None
            mock_request = MagicMock()
            result = await api_mod.verify_worker_jwt(mock_request)
            assert result is None  # auth bypassed
            captured = capsys.readouterr()
            assert "SECURITY" in captured.out
            assert "JWT_SECRET" in captured.out
        finally:
            api_mod.JWT_SECRET = original_secret
            api_mod._jwt_warning_logged = False

    @pytest.mark.asyncio
    async def test_jwt_warning_logged_only_once(self, capsys):
        """The warning should only fire once per process, not spam logs."""
        import interfaces.api as api_mod

        api_mod._jwt_warning_logged = False
        original_secret = api_mod.JWT_SECRET
        try:
            api_mod.JWT_SECRET = None
            mock_request = MagicMock()

            await api_mod.verify_worker_jwt(mock_request)
            await api_mod.verify_worker_jwt(mock_request)
            await api_mod.verify_worker_jwt(mock_request)

            captured = capsys.readouterr()
            # The warning text "JWT_SECRET" should appear exactly once
            assert captured.out.count("JWT_SECRET") == 1
        finally:
            api_mod.JWT_SECRET = original_secret
            api_mod._jwt_warning_logged = False


# ================================================================
# 5. Approval Idempotency Guard
# ================================================================


class TestApprovalIdempotency:
    """Verify the worker_task_input endpoint rejects double-submissions."""

    @pytest.mark.asyncio
    async def test_input_rejected_for_terminal_task(self):
        """If a task is already completed, submitting approval should return current state."""
        from interfaces.api import app
        from httpx import AsyncClient, ASGITransport

        completed_task = {
            "task_id": "test-idempotency-123",
            "chat_id": "test_chat",
            "source": "http",
            "status": "completed",
            "awaiting_response": False,
            "id": "op1",
            "plan": None,
            "diffs": {},
            "user_input": "test",
            "files_to_modify": [],
            "created_at": "2026-01-01T00:00:00Z",
            "last_response": "Done",
            "dry_run": False,
            "test_mode": False,
            "awaiting_type": None,
        }

        with patch("interfaces.api.find_session_by_task_id", return_value=("test_chat", "http")), \
             patch("interfaces.api.get_active_task_id", return_value="test-idempotency-123"), \
             patch("interfaces.api.find_task_by_id", return_value=completed_task), \
             patch("interfaces.api.db_get_task", return_value=completed_task), \
             patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.post(
                    "/worker/task/test-idempotency-123/input",
                    json={"approval": True},
                )
            # process_message should NOT have been called (idempotency guard)
            mock_pm.assert_not_called()
            assert resp.status_code == 200
            data = resp.json()
            assert data["task_id"] == "test-idempotency-123"

    @pytest.mark.asyncio
    async def test_input_rejected_for_failed_task(self):
        """If a task has failed, submitting input should return current state, not re-process."""
        from interfaces.api import app
        from httpx import AsyncClient, ASGITransport

        failed_task = {
            "task_id": "test-failed-789",
            "chat_id": "test_chat",
            "source": "http",
            "status": "failed",
            "awaiting_response": False,
            "id": "op3",
            "plan": None,
            "diffs": {},
            "user_input": "test",
            "files_to_modify": [],
            "created_at": "2026-01-01T00:00:00Z",
            "last_response": "Error",
            "dry_run": False,
            "test_mode": False,
            "awaiting_type": None,
        }

        with patch("interfaces.api.find_session_by_task_id", return_value=("test_chat", "http")), \
             patch("interfaces.api.get_active_task_id", return_value="test-failed-789"), \
             patch("interfaces.api.find_task_by_id", return_value=failed_task), \
             patch("interfaces.api.db_get_task", return_value=failed_task), \
             patch("interfaces.api.process_message", new_callable=AsyncMock) as mock_pm:

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.post(
                    "/worker/task/test-failed-789/input",
                    json={"approval": True},
                )
            mock_pm.assert_not_called()
            assert resp.status_code == 200

    @pytest.mark.asyncio
    async def test_input_allowed_for_awaiting_task(self):
        """Tasks that are awaiting input should still be processable."""
        from interfaces.api import app
        from httpx import AsyncClient, ASGITransport

        awaiting_task = {
            "task_id": "test-awaiting-456",
            "chat_id": "test_chat",
            "source": "http",
            "status": "planning",
            "awaiting_response": True,
            "awaiting_type": "approval",
            "id": "op2",
            "plan": {"steps": []},
            "diffs": {},
            "user_input": "test",
            "files_to_modify": [],
            "created_at": "2026-01-01T00:00:00Z",
            "last_response": "Approve?",
            "dry_run": False,
            "test_mode": False,
        }

        result_task = dict(awaiting_task)
        result_task["status"] = "completed"
        result_task["awaiting_response"] = False

        with patch("interfaces.api.find_session_by_task_id", return_value=("test_chat", "http")), \
             patch("interfaces.api.get_active_task_id", return_value="test-awaiting-456"), \
             patch("interfaces.api.find_task_by_id", side_effect=[awaiting_task, result_task]), \
             patch("interfaces.api.db_get_task", return_value=awaiting_task), \
             patch("interfaces.api.process_message", new_callable=AsyncMock, return_value=("OK", False, None)), \
             patch("interfaces.api.get_current_status", return_value="completed"), \
             patch("interfaces.api.update_operation_status"), \
             patch("interfaces.api.load_state", return_value={"task_queue": []}):

            async with AsyncClient(
                transport=ASGITransport(app=app),
                base_url="http://test",
            ) as client:
                resp = await client.post(
                    "/worker/task/test-awaiting-456/input",
                    json={"approval": True},
                )
            assert resp.status_code == 200
