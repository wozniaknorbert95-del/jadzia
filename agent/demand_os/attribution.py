"""K1 REV_R1 — wizard_start attribution (SQLite authority, fail-closed).

Contract v1 fields: event_id, ts_utc, source, medium, campaign, content/asset,
landing_url, session_or_anon_id, provenance, dedupe_key, attribution_status.
"""

from __future__ import annotations

import hashlib
import json
import logging
import sqlite3
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from urllib.parse import parse_qs, urlparse

logger = logging.getLogger(__name__)

CONTRACT_VERSION = "rev_r1.v1"
ATTRIBUTION_STATUSES = ("attributed", "unattributed", "ambiguous", "unavailable")


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _db_path() -> Path:
    import os

    env = os.getenv("JADZIA_DB_PATH") or os.getenv("DATABASE_PATH")
    if env:
        return Path(env)
    return Path(__file__).resolve().parents[2] / "data" / "jadzia.db"


def ensure_attribution_schema(conn: sqlite3.Connection, *, commit: bool = False) -> None:
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS demand_wizard_starts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            event_id TEXT NOT NULL UNIQUE,
            dedupe_key TEXT NOT NULL UNIQUE,
            ts_utc TEXT NOT NULL,
            source TEXT,
            medium TEXT,
            campaign TEXT,
            content TEXT,
            asset_id TEXT,
            channel TEXT,
            landing_url TEXT,
            session_or_anon_id TEXT,
            provenance TEXT NOT NULL,
            attribution_status TEXT NOT NULL
                CHECK (attribution_status IN (
                    'attributed','unattributed','ambiguous','unavailable'
                )),
            utm_link TEXT,
            payload_json TEXT NOT NULL DEFAULT '{}',
            created_at TEXT NOT NULL
        )
        """
    )
    conn.execute(
        """
        CREATE INDEX IF NOT EXISTS idx_demand_wizard_starts_ts
        ON demand_wizard_starts(ts_utc DESC)
        """
    )
    if commit:
        conn.commit()


def parse_utm(utm_link: str) -> Dict[str, str]:
    qs = parse_qs(urlparse(utm_link or "").query)
    def _one(key: str) -> str:
        vals = qs.get(key) or []
        return (vals[0] if vals else "").strip()

    return {
        "source": _one("utm_source"),
        "medium": _one("utm_medium"),
        "campaign": _one("utm_campaign"),
        "content": _one("utm_content"),
    }


def resolve_attribution_status(
    *,
    asset_id: str,
    utm_parts: Dict[str, str],
    calendar_assets: Optional[set] = None,
) -> str:
    content = (utm_parts.get("content") or "").strip()
    aid = (asset_id or content or "").strip()
    if not aid:
        return "unattributed"
    if not (utm_parts.get("source") and utm_parts.get("medium")):
        return "unattributed"
    if calendar_assets is not None:
        if aid in calendar_assets:
            return "attributed"
        if content and content != aid and content in calendar_assets:
            return "ambiguous"
        return "unattributed"
    return "attributed" if aid else "unattributed"


def build_dedupe_key(
    *,
    provenance: str,
    source_event_id: str,
    utm_link: str,
    ts_utc: str,
) -> str:
    raw = f"{provenance}|{source_event_id}|{utm_link}|{ts_utc}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def ingest_wizard_start_event(
    *,
    event_id: str,
    ts_utc: str,
    utm_link: str,
    asset_id: str = "",
    channel: str = "",
    landing_url: str = "",
    session_or_anon_id: str = "",
    provenance: str = "ops_bus",
    source_event_id: str = "",
    calendar_assets: Optional[set] = None,
    db_path: Optional[Path] = None,
) -> Dict[str, Any]:
    """Insert deduped wizard_start. Retry with same dedupe_key is no-op success."""
    path = db_path or _db_path()
    path.parent.mkdir(parents=True, exist_ok=True)
    utm_parts = parse_utm(utm_link)
    aid = (asset_id or utm_parts.get("content") or "").strip()
    status = resolve_attribution_status(
        asset_id=aid, utm_parts=utm_parts, calendar_assets=calendar_assets
    )
    dedupe = build_dedupe_key(
        provenance=provenance,
        source_event_id=source_event_id or event_id,
        utm_link=utm_link,
        ts_utc=ts_utc,
    )
    payload = {
        "contract": CONTRACT_VERSION,
        "utm": utm_parts,
        "asset_id": aid,
    }
    conn = sqlite3.connect(str(path))
    try:
        ensure_attribution_schema(conn, commit=False)
        existing = conn.execute(
            "SELECT event_id, attribution_status FROM demand_wizard_starts WHERE dedupe_key = ?",
            (dedupe,),
        ).fetchone()
        if existing:
            return {
                "ok": True,
                "duplicate": True,
                "event_id": existing[0],
                "attribution_status": existing[1],
                "dedupe_key": dedupe,
            }
        conn.execute(
            """
            INSERT INTO demand_wizard_starts (
                event_id, dedupe_key, ts_utc, source, medium, campaign, content,
                asset_id, channel, landing_url, session_or_anon_id, provenance,
                attribution_status, utm_link, payload_json, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                dedupe,
                ts_utc,
                utm_parts.get("source"),
                utm_parts.get("medium"),
                utm_parts.get("campaign"),
                utm_parts.get("content"),
                aid,
                channel,
                landing_url or utm_link,
                session_or_anon_id,
                provenance,
                status,
                utm_link,
                json.dumps(payload, ensure_ascii=False),
                _utc_now(),
            ),
        )
        conn.commit()
        return {
            "ok": True,
            "duplicate": False,
            "event_id": event_id,
            "attribution_status": status,
            "dedupe_key": dedupe,
            "asset_id": aid,
        }
    finally:
        conn.close()


def sync_ops_bus_to_attribution(
    *,
    limit: int = 50,
    db_path: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """ops_bus wizard_started → demand_wizard_starts (SQLite authority)."""
    try:
        from agent.db import db_ops_bus_list
    except Exception as exc:
        return {"ok": False, "mode": "no_db", "synced": 0, "error": str(exc)[:200]}

    try:
        rows = db_ops_bus_list(event_type="wizard_started", limit=limit) or []
    except Exception as exc:
        return {"ok": False, "mode": "db_error", "synced": 0, "error": str(exc)[:200]}

    synced = 0
    duplicates = 0
    errors: List[str] = []
    details: List[Dict[str, Any]] = []

    for row in rows:
        payload = row.get("payload") or row.get("payload_json") or {}
        if isinstance(payload, str):
            try:
                payload = json.loads(payload)
            except json.JSONDecodeError:
                payload = {}
        utm = (payload.get("utm_link") or payload.get("url") or "").strip()
        if not utm:
            errors.append("missing utm")
            continue
        event_id = str(row.get("event_id") or f"ops_{row.get('id')}")
        ts = str(row.get("created_at") or _utc_now())
        asset_id = str(payload.get("asset_id") or payload.get("utm_content") or "")
        if dry_run:
            details.append({"event_id": event_id, "utm_link": utm, "dry_run": True})
            synced += 1
            continue
        try:
            result = ingest_wizard_start_event(
                event_id=event_id,
                ts_utc=ts,
                utm_link=utm,
                asset_id=asset_id,
                channel=str(payload.get("utm_source") or payload.get("channel") or ""),
                landing_url=utm,
                session_or_anon_id=str(payload.get("session_id") or ""),
                provenance="ops_bus",
                source_event_id=str(row.get("source_event_id") or event_id),
                db_path=db_path,
            )
            if result.get("duplicate"):
                duplicates += 1
            else:
                synced += 1
            details.append(result)
        except Exception as exc:
            errors.append(str(exc)[:120])

    return {
        "ok": True,
        "mode": "ops_bus_attribution",
        "synced": synced,
        "duplicates": duplicates,
        "errors": errors[:20],
        "details": details[:20],
        "dry_run": dry_run,
        "contract": CONTRACT_VERSION,
    }


def attribution_summary(
    *,
    db_path: Optional[Path] = None,
    days: int = 7,
) -> Dict[str, Any]:
    path = db_path or _db_path()
    window_days = max(1, min(int(days or 7), 90))
    if not path.is_file():
        return {
            "ok": True,
            "status": "unavailable",
            "total": 0,
            "by_status": {},
            "top_assets": [],
            "window_days": window_days,
            "contract": CONTRACT_VERSION,
        }
    cutoff = (datetime.now(timezone.utc) - timedelta(days=window_days)).isoformat()
    conn = sqlite3.connect(str(path))
    try:
        ensure_attribution_schema(conn, commit=False)
        rows = conn.execute(
            """
            SELECT attribution_status, COUNT(*)
            FROM demand_wizard_starts
            WHERE ts_utc >= ?
            GROUP BY attribution_status
            """,
            (cutoff,),
        ).fetchall()
        by_status = {r[0]: int(r[1]) for r in rows}
        total = sum(by_status.values())
        top = conn.execute(
            """
            SELECT asset_id, COUNT(*) AS n
            FROM demand_wizard_starts
            WHERE asset_id IS NOT NULL AND asset_id != ''
              AND ts_utc >= ?
            GROUP BY asset_id
            ORDER BY n DESC
            LIMIT 5
            """,
            (cutoff,),
        ).fetchall()
        return {
            "ok": True,
            "status": "ok" if total else "unavailable",
            "total": total,
            "by_status": by_status,
            "top_assets": [{"asset_id": r[0], "starts": int(r[1])} for r in top],
            "window_days": window_days,
            "contract": CONTRACT_VERSION,
        }
    finally:
        conn.close()
