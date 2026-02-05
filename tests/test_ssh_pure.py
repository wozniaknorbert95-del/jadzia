"""
Tests for pure SSH I/O (agent.tools.ssh_pure).
Uses mocks for paramiko so no real SSH is required.
"""

import pytest
from unittest.mock import MagicMock, patch

from agent.tools.ssh_pure import (
    read_file_ssh,
    write_file_ssh,
    get_path_type_ssh,
    exec_command_ssh,
    list_directory_ssh,
    SSHConnection,
    ConnectionError,
)


@pytest.fixture
def mock_paramiko():
    """Mock paramiko SSHClient and SFTP so no real connection is made."""
    with patch("agent.tools.ssh_pure.SSHConnection") as mock_conn_class:
        conn = MagicMock()
        mock_conn_class.return_value.__enter__ = MagicMock(return_value=conn)
        mock_conn_class.return_value.__exit__ = MagicMock(return_value=None)
        yield conn


def test_read_file_ssh_returns_decoded_content(mock_paramiko):
    """read_file_ssh returns string content decoded from UTF-8."""
    mock_paramiko.sftp.open.return_value.__enter__ = MagicMock(
        return_value=MagicMock(read=MagicMock(return_value=b"hello \xc5\x9bwiat"))
    )
    mock_paramiko.sftp.open.return_value.__exit__ = MagicMock(return_value=None)
    result = read_file_ssh("host", 22, "user", "pass", "/remote/path")
    assert result == "hello \u015bwiat"
    mock_paramiko.sftp.open.assert_called_once_with("/remote/path", "r")


def test_write_file_ssh_writes_utf8(mock_paramiko):
    """write_file_ssh encodes content as UTF-8 and writes."""
    mock_file = MagicMock()
    mock_paramiko.sftp.open.return_value.__enter__ = MagicMock(return_value=mock_file)
    mock_paramiko.sftp.open.return_value.__exit__ = MagicMock(return_value=None)
    result = write_file_ssh("host", 22, "user", "pass", "/remote/file.txt", "test \u015b", None)
    assert result is True
    mock_file.write.assert_called_once_with("test \u015b".encode("utf-8"))


def test_get_path_type_ssh_returns_file(mock_paramiko):
    """get_path_type_ssh returns 'file' when path is a regular file."""
    import stat
    mock_paramiko.sftp.stat.return_value = MagicMock(st_mode=stat.S_IFREG | 0o644)
    result = get_path_type_ssh("host", 22, "user", "pass", "/remote/file.txt")
    assert result == "file"


def test_get_path_type_ssh_returns_not_found(mock_paramiko):
    """get_path_type_ssh returns 'not_found' when path does not exist."""
    mock_paramiko.sftp.stat.side_effect = FileNotFoundError()
    result = get_path_type_ssh("host", 22, "user", "pass", "/remote/missing")
    assert result == "not_found"


def test_exec_command_ssh_returns_stdout_stderr(mock_paramiko):
    """exec_command_ssh returns (success, stdout, stderr)."""
    mock_paramiko.exec_command.return_value = ("out", "")
    success, stdout, stderr = exec_command_ssh("host", 22, "user", "pass", "echo ok")
    assert success is True
    assert "out" in stdout
    assert stderr == ""
