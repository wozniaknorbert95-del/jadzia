"""Demand OS Memory — OS TARGET §F three layers (file-backed v0).

Semantic (ICP) · Episodic (what drove starts) · Procedural (sniper playbook pointer).
"""

from __future__ import annotations

import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import logging

from agent.demand_os.observability import build_screen, money_check

logger = logging.getLogger(__name__)


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _set_now() -> Path:
    env = os.environ.get("DEMAND_OS_SET_NOW")
    if env:
        return Path(env)
    return _repo_root() / "docs" / "ops" / "demand-os" / "set-now"


def default_memory_path() -> Path:
    """Resolve MEMORY path via the shared writable-path contract."""
    from agent.demand_os.state_paths import resolve_writable_path

    return resolve_writable_path("MEMORY.json", env_var="DEMAND_OS_MEMORY")


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _empty_store() -> Dict[str, Any]:
    return {
        "updated": _utc_now(),
        "semantic": {
            "icp_role_week": "installateur",
            "hook_nl": "witte bus · opdrachtgever ziet je niet",
            "cta": "wizard_only",
        },
        "episodic": {
            "top_hook_asset_id": "",
            "starts_utm_total": 0,
            "weekly_improvement": "",
            "history": [],
        },
        "procedural": {
            "playbook": "docs/ops/SYSTEM-FIRM-OPERATING-SYSTEM-TARGET.md",
            "validator_rules": "C.5 R1-R8",
            "anti_spam": "<=1 group/copy/day",
            "ads": "parked_cash until budget+GO",
        },
    }


def load_memory(*, path: Optional[Path] = None) -> Dict[str, Any]:
    p = path or default_memory_path()
    if not p.is_file():
        return _empty_store()
    try:
        data = json.loads(p.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return _empty_store()
    base = _empty_store()
    for k in ("semantic", "episodic", "procedural"):
        if isinstance(data.get(k), dict):
            base[k].update(data[k])
    base["updated"] = data.get("updated") or base["updated"]
    return base


def save_memory(store: Dict[str, Any], *, path: Optional[Path] = None) -> Path:
    p = path or default_memory_path()
    store["updated"] = _utc_now()
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(store, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        logger.info("save_memory ok path=%s", p)
    except OSError as exc:
        logger.error(
            "save_memory skipped read_only=true path=%s err=%s hint=set DEMAND_OS_MEMORY writable",
            p,
            exc,
        )
    return p


def sync_episodic_from_ledger(
    *,
    set_now: Optional[Path] = None,
    memory_path: Optional[Path] = None,
    weekly_improvement: str = "",
) -> Dict[str, Any]:
    """Refresh episodic layer from ledger/observability (OS §F weekly tip)."""
    mc = money_check(set_now=set_now)
    screen = build_screen(set_now=set_now)
    store = load_memory(path=memory_path)
    top = mc.get("top_hook") or screen.top_hook or ""
    entry = {
        "ts": _utc_now(),
        "top_hook_asset_id": top,
        "starts_utm_total": mc.get("starts_utm") or 0,
        "paid": mc.get("paid") or 0,
        "validator_fail": mc.get("validator_fail") or 0,
    }
    store["episodic"]["top_hook_asset_id"] = top
    store["episodic"]["starts_utm_total"] = entry["starts_utm_total"]
    if weekly_improvement:
        store["episodic"]["weekly_improvement"] = weekly_improvement
    hist: List[Dict[str, Any]] = list(store["episodic"].get("history") or [])
    hist.append(entry)
    store["episodic"]["history"] = hist[-52:]  # keep ~1y weekly
    save_memory(store, path=memory_path)
    return store


def set_semantic_icp(
    role: str,
    hook_nl: str,
    *,
    memory_path: Optional[Path] = None,
    emit_a2a: bool = True,
) -> Dict[str, Any]:
    store = load_memory(path=memory_path)
    store["semantic"]["icp_role_week"] = role
    store["semantic"]["hook_nl"] = hook_nl
    store["semantic"]["cta"] = "wizard_only"
    save_memory(store, path=memory_path)
    if emit_a2a:
        try:
            from agent.demand_os.a2a_bus import ack_handoff, emit_handoff
            from agent.demand_os.audit_log import append_audit

            emitted = emit_handoff(
                "brief_icp",
                asset_id=f"icp_{role}",
                from_agent="Growth_Lead",
                to_agent="ICP_Brain",
                payload={"icp_role": role, "hook_nl": hook_nl},
            )
            ack_handoff(emitted["id"])
            append_audit(
                "brief_icp",
                actor="Growth_Lead",
                detail={"role": role, "handoff_id": emitted["id"]},
            )
            store["last_brief_icp_id"] = emitted["id"]
        except Exception:
            pass
    return store
