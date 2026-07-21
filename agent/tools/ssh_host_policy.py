"""Strict known-host and optional fingerprint policy for Paramiko clients."""

from __future__ import annotations

import base64
import hashlib
import hmac
import os
from typing import Any


class HostKeyVerificationError(Exception):
    """Raised when the configured SSH host key cannot be trusted."""


def configure_host_key_policy(client: Any, known_hosts_path: str | None = None) -> None:
    """Load trusted host keys and reject unknown hosts."""
    import paramiko

    client.load_system_host_keys()
    configured_path = known_hosts_path or os.getenv("SSH_KNOWN_HOSTS_PATH", "")
    if configured_path:
        if not os.path.isfile(configured_path):
            raise HostKeyVerificationError("Configured SSH known_hosts file does not exist.")
        client.load_host_keys(configured_path)
    client.set_missing_host_key_policy(paramiko.RejectPolicy())


def verify_host_key_fingerprint(client: Any, expected: str | None = None) -> None:
    """Verify an optional SHA256 host-key pin after a trusted connection."""
    configured = expected or os.getenv("SSH_HOST_KEY_FINGERPRINT", "")
    if not configured:
        return

    transport = client.get_transport()
    remote_key = transport.get_remote_server_key() if transport else None
    if remote_key is None:
        raise HostKeyVerificationError("SSH transport did not provide a host key.")
    actual = base64.b64encode(hashlib.sha256(remote_key.asbytes()).digest()).decode().rstrip("=")
    normalized = configured.removeprefix("SHA256:").rstrip("=")
    if not hmac.compare_digest(actual, normalized):
        raise HostKeyVerificationError(
            "SSH host key fingerprint does not match the configured pin."
        )
