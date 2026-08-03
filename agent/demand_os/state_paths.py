"""Writable state path resolution — one contract for all Demand OS runtime files.

Prod deploy checkout (`docs/ops/demand-os/set-now/`) is read-only for the
service user. Any module that WRITES runtime state must resolve its path via
`resolve_writable_path`: env override → writable set-now → `data/demand-os/`
fallback (logged once per resolution, same pattern as memory/heartbeat).

Read-only lookups (SoT shipped in repo) do NOT belong here — fallback would
silently hide deploy content. Only writers fall back.
"""

from __future__ import annotations

import logging
import os
from pathlib import Path

logger = logging.getLogger(__name__)

_REPO = Path(__file__).resolve().parents[2]
_SET_NOW_REL = Path("docs/ops/demand-os/set-now")
_FALLBACK_DIR = _REPO / "data" / "demand-os"


def resolve_writable_path(filename: str, *, env_var: str | None = None) -> Path:
    """Resolve a writable runtime file path.

    Order: `env_var` (explicit override, e.g. tests) → writable set-now dir →
    `data/demand-os/<filename>` fallback with a warning (prod contract).
    """
    if env_var:
        env = os.environ.get(env_var)
        if env:
            return Path(env)
    set_now = _REPO / _SET_NOW_REL
    try:
        set_now.mkdir(parents=True, exist_ok=True)
        probe = set_now / ".write_probe"
        probe.write_text("", encoding="utf-8")
        probe.unlink(missing_ok=True)
        return set_now / filename
    except OSError as exc:
        fallback = _FALLBACK_DIR / filename
        logger.warning(
            "STATE path fallback set_now_unwritable path=%s fallback=%s err=%s",
            set_now / filename,
            fallback,
            exc,
        )
        return fallback
