"""Negative security tests for SSH trust and archive extraction."""

import base64
import hashlib
import io
import tarfile
from unittest.mock import Mock, patch

import pytest

from agent.tools.safe_archive import UnsafeArchiveError, extract_tar_safely
from agent.tools.ssh_host_policy import (
    HostKeyVerificationError,
    configure_host_key_policy,
    verify_host_key_fingerprint,
)
from agent.tools.ssh_orchestrator import list_files


def test_host_policy_loads_known_hosts_and_rejects_unknown_hosts() -> None:
    client = Mock()
    with (
        patch("agent.tools.ssh_host_policy.os.path.isfile", return_value=True),
        patch("paramiko.RejectPolicy") as reject_policy,
    ):
        configure_host_key_policy(client, known_hosts_path="/tmp/known_hosts")

    client.load_system_host_keys.assert_called_once()
    client.load_host_keys.assert_called_once_with("/tmp/known_hosts")
    client.set_missing_host_key_policy.assert_called_once_with(reject_policy.return_value)


def test_host_policy_rejects_missing_configured_known_hosts() -> None:
    with patch("agent.tools.ssh_host_policy.os.path.isfile", return_value=False):
        with pytest.raises(HostKeyVerificationError, match="does not exist"):
            configure_host_key_policy(Mock(), known_hosts_path="/missing/known_hosts")


def test_host_key_pin_rejects_changed_key() -> None:
    remote_key = Mock()
    remote_key.asbytes.return_value = b"changed-host-key"
    client = Mock()
    client.get_transport.return_value.get_remote_server_key.return_value = remote_key

    with pytest.raises(HostKeyVerificationError, match="does not match"):
        verify_host_key_fingerprint(client, expected="SHA256:not-the-remote-key")


def test_host_key_pin_accepts_matching_key() -> None:
    key_bytes = b"trusted-host-key"
    expected = base64.b64encode(hashlib.sha256(key_bytes).digest()).decode().rstrip("=")
    remote_key = Mock()
    remote_key.asbytes.return_value = key_bytes
    client = Mock()
    client.get_transport.return_value.get_remote_server_key.return_value = remote_key

    verify_host_key_fingerprint(client, expected=f"SHA256:{expected}")


def test_extract_tar_safely_rejects_path_traversal(tmp_path) -> None:
    archive_path = tmp_path / "unsafe.tar"
    with tarfile.open(archive_path, "w") as archive:
        member = tarfile.TarInfo("../../outside.txt")
        member.size = 1
        archive.addfile(member, io.BytesIO(b"x"))

    with tarfile.open(archive_path, "r") as archive:
        with pytest.raises(UnsafeArchiveError, match="escapes"):
            extract_tar_safely(archive, tmp_path / "output")


def test_list_files_rejects_shell_injection_before_execution() -> None:
    with patch("agent.tools.ssh_orchestrator.exec_command_ssh") as execute:
        with pytest.raises(ValueError, match="without path separators"):
            list_files("'; rm -rf / #")

    execute.assert_not_called()
