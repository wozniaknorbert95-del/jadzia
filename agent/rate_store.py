"""File-backed rate limit buckets — survives jadzia process restart (F-080/F-043)."""

from __future__ import annotations

import json
import os
import threading
import time
from pathlib import Path

_lock = threading.Lock()
_memory: dict[str, list[float]] | None = None


def _store_path() -> Path:
    raw = os.getenv("DA_RATE_STORE_PATH", "/tmp/da-rate-store.json")
    return Path(raw)


def _load_locked() -> dict[str, list[float]]:
    global _memory
    if _memory is not None:
        return _memory
    path = _store_path()
    if path.exists():
        try:
            raw = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(raw, dict):
                _memory = {
                    str(k): [float(t) for t in v if isinstance(t, (int, float))]
                    for k, v in raw.items()
                    if isinstance(v, list)
                }
                return _memory
        except (OSError, json.JSONDecodeError, TypeError, ValueError):
            pass
    _memory = {}
    return _memory


def _save_locked(store: dict[str, list[float]]) -> None:
    path = _store_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(store), encoding="utf-8")


def check_and_record(bucket: str, *, window_sec: int, limit: int) -> None:
    """Raise ValueError('RATE_LIMIT') when bucket is over limit; else record hit."""
    now = time.time()
    with _lock:
        store = _load_locked()
        hits = [t for t in store.get(bucket, []) if now - t < window_sec]
        if len(hits) >= limit:
            raise ValueError("RATE_LIMIT")
        hits.append(now)
        store[bucket] = hits
        global _memory
        _memory = store
        _save_locked(store)


def clear_store() -> None:
    """Test helper — wipe in-memory and on-disk rate data."""
    global _memory
    with _lock:
        _memory = {}
        path = _store_path()
        if path.exists():
            path.unlink()


def reset_memory_cache() -> None:
    """Test helper — force reload from disk on next access."""
    global _memory
    with _lock:
        _memory = None
