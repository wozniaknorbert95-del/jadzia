"""Control plane audit — OS §G (append-only JSONL, local)."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional
from uuid import uuid4

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_AUDIT = _REPO / "docs/ops/demand-os/set-now/CONTROL-AUDIT.jsonl"


def _utc() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def append_audit(
    action: str,
    *,
    actor: str = "agent",
    detail: Optional[Dict[str, Any]] = None,
    path: Optional[Path] = None,
) -> Dict[str, Any]:
    dest = path or DEFAULT_AUDIT
    dest.parent.mkdir(parents=True, exist_ok=True)
    rec = {
        "id": f"aud_{uuid4().hex[:12]}",
        "ts": _utc(),
        "action": action,
        "actor": actor,
        "detail": detail or {},
    }
    with dest.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, ensure_ascii=True) + "\n")
    return rec


def list_audit(*, limit: int = 50, path: Optional[Path] = None) -> Dict[str, Any]:
    src = path or DEFAULT_AUDIT
    if not src.is_file():
        return {"ok": True, "items": [], "count": 0}
    lines = src.read_text(encoding="utf-8").splitlines()
    items = []
    for line in lines[-limit:]:
        try:
            items.append(json.loads(line))
        except json.JSONDecodeError:
            continue
    return {"ok": True, "items": items, "count": len(items), "path": str(src)}
