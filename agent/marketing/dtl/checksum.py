"""Stable checksum helpers for append-only raw ingest."""

from __future__ import annotations

import hashlib
import json
from typing import Any


def payload_checksum(payload: Any) -> str:
    """SHA-256 of canonical JSON (sorted keys)."""
    blob = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return hashlib.sha256(blob.encode("utf-8")).hexdigest()
