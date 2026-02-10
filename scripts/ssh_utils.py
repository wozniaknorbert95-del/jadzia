"""
SSH key checks before connecting (e.g. to VPS 185.243.54.115).
Raises a concrete exception if the key file is missing instead of blocking on interactive password.
"""

import os
from pathlib import Path


class SSHKeyNotFoundError(FileNotFoundError):
    """Raised when the SSH private key file is missing or not a regular file."""

    def __init__(self, path: str, host: str = "185.243.54.115", message: str = ""):
        self.path = path
        self.host = host
        msg = message or (
            f"SSH key not found: {path}. Cannot connect to {host} without key."
        )
        super().__init__(msg)


def ensure_ssh_key(
    key_path: str = "/root/.ssh/cyberfolks_key",
    host: str = "185.243.54.115",
) -> str:
    """
    Verify that the SSH private key file exists and is a regular file.
    Returns the resolved key_path. Raises SSHKeyNotFoundError if missing or not a file.
    """
    path = os.path.expanduser(key_path)
    if not os.path.exists(path):
        raise SSHKeyNotFoundError(path, host=host)
    if not os.path.isfile(path):
        raise SSHKeyNotFoundError(
            path,
            host=host,
            message=f"Path is not a file: {path}",
        )
    return path


def chmod_ssh_keys_instructions(ssh_dir: str = "~/.ssh") -> str:
    """
    Return instructions for setting correct permissions (600) on private keys.
    Use when key exists but connection fails due to permissions.
    """
    d = os.path.expanduser(ssh_dir)
    return (
        f"Recommended: chmod 700 {d}\n"
        f"  chmod 600 {d}/cyberfolks_key\n"
        "  # Or all private keys (no .pub): "
        f"for f in {d}/*; do [ -f \"$f\" ] && [ \"${{f%.pub}}\" = \"$f\" ] && chmod 600 \"$f\"; done"
    )
