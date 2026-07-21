"""Validation for outbound worker callback URLs."""

from __future__ import annotations

import ipaddress
import os
import socket
from urllib.parse import SplitResult, urlsplit

MAX_CALLBACK_URL_LENGTH = 2048


class CallbackUrlError(ValueError):
    """Raised when a callback URL is unsafe or not registered."""


def _allowlisted_hosts() -> set[str]:
    raw = os.getenv("WEBHOOK_CALLBACK_ALLOWLIST", "")
    return {host.strip().lower().rstrip(".") for host in raw.split(",") if host.strip()}


def _parse_callback_url(value: str) -> SplitResult:
    if not value or not value.strip():
        raise CallbackUrlError("Callback URL cannot be empty.")
    if len(value) > MAX_CALLBACK_URL_LENGTH:
        raise CallbackUrlError("Callback URL exceeds the maximum length.")

    parsed = urlsplit(value)
    if parsed.scheme != "https":
        raise CallbackUrlError("Callback URL must use HTTPS.")
    if not parsed.hostname:
        raise CallbackUrlError("Callback URL must include a hostname.")
    if parsed.username or parsed.password or parsed.fragment:
        raise CallbackUrlError("Callback URL contains unsupported components.")
    try:
        parsed.port
    except ValueError as exc:
        raise CallbackUrlError("Callback URL contains an invalid port.") from exc
    return parsed


def _resolve_addresses(hostname: str) -> set[str]:
    try:
        results = socket.getaddrinfo(hostname, None, type=socket.SOCK_STREAM)
    except socket.gaierror as exc:
        raise CallbackUrlError("Callback hostname could not be resolved.") from exc
    return {str(result[4][0]) for result in results}


def _require_public_addresses(hostname: str) -> None:
    addresses = _resolve_addresses(hostname)
    if not addresses:
        raise CallbackUrlError("Callback hostname has no resolved addresses.")
    for address in addresses:
        try:
            ip = ipaddress.ip_address(address)
        except ValueError as exc:
            raise CallbackUrlError("Callback hostname resolved to an invalid address.") from exc
        if not ip.is_global:
            raise CallbackUrlError("Callback hostname resolves to a non-public address.")


def validate_callback_url(value: str | None) -> str | None:
    """Allow only registered HTTPS endpoints resolving exclusively to public IPs."""
    if value is None:
        return None

    normalized = value.strip()
    parsed = _parse_callback_url(normalized)
    hostname_raw = parsed.hostname
    if hostname_raw is None:
        raise CallbackUrlError("Callback URL must include a hostname.")
    hostname = hostname_raw.lower().rstrip(".")
    if hostname not in _allowlisted_hosts():
        raise CallbackUrlError("Callback hostname is not allowlisted.")
    _require_public_addresses(hostname)
    return normalized


def redact_callback_url(value: str) -> str:
    """Return a log-safe callback target without path, query, or credentials."""
    parsed = urlsplit(value)
    if not parsed.hostname:
        return "<invalid-callback>"
    port = f":{parsed.port}" if parsed.port else ""
    return f"{parsed.scheme}://{parsed.hostname}{port}"
