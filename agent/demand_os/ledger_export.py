"""K13 — Deterministic LEDGER projection from SQLite attribution authority."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.desk_contract import set_now_path

EXPORTER_VERSION = "k13.v1"
LEDGER_FIELDS = [
    "date",
    "asset_id",
    "channel",
    "utm_link",
    "wizard_starts",
    "publish_Y/N",
    "comments_sent",
    "paid",
    "notes",
]


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build_ledger_rows_from_sqlite(*, db_path: Optional[Path] = None) -> List[Dict[str, str]]:
    import sqlite3

    from agent.demand_os.attribution import _db_path, ensure_attribution_schema

    path = db_path or _db_path()
    if not path.is_file():
        return []
    conn = sqlite3.connect(str(path))
    try:
        ensure_attribution_schema(conn, commit=False)
        rows = conn.execute(
            """
            SELECT substr(ts_utc, 1, 10) AS d, asset_id, channel, utm_link, COUNT(*) AS n
            FROM demand_wizard_starts
            GROUP BY d, asset_id, channel, utm_link
            ORDER BY d, asset_id
            """
        ).fetchall()
    finally:
        conn.close()
    out: List[Dict[str, str]] = []
    for d, asset_id, channel, utm_link, n in rows:
        out.append(
            {
                "date": d or date.today().isoformat(),
                "asset_id": asset_id or "",
                "channel": channel or "",
                "utm_link": utm_link or "",
                "wizard_starts": str(int(n)),
                "publish_Y/N": "N",
                "comments_sent": "0",
                "paid": "0",
                "notes": f"export {EXPORTER_VERSION} attribution",
            }
        )
    return out


def render_ledger_csv(rows: List[Dict[str, str]]) -> str:
    from io import StringIO

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=LEDGER_FIELDS, lineterminator="\n")
    writer.writeheader()
    for row in rows:
        writer.writerow({k: row.get(k, "") for k in LEDGER_FIELDS})
    return buf.getvalue()


def export_ledger(
    *,
    set_now: Optional[Path] = None,
    db_path: Optional[Path] = None,
    dry_run: bool = True,
) -> Dict[str, Any]:
    root = set_now or set_now_path()
    rows = build_ledger_rows_from_sqlite(db_path=db_path)
    body = render_ledger_csv(rows)
    checksum = _sha256_bytes(body.encode("utf-8"))
    watermark = checksum[:16]
    manifest = {
        "exporter": EXPORTER_VERSION,
        "generated_at": _utc_now(),
        "row_count": len(rows),
        "checksum_sha256": checksum,
        "watermark": watermark,
        "authority": "sqlite:demand_wizard_starts",
        "dry_run": dry_run,
        "target": str(root / "LEDGER.csv"),
    }
    if dry_run:
        return {"ok": True, "manifest": manifest, "preview_rows": len(rows), "applied": False}

    root.mkdir(parents=True, exist_ok=True)
    target = root / "LEDGER.csv"
    backup = root / f"LEDGER.csv.bak.{watermark}"
    if target.is_file():
        shutil.copy2(target, backup)
    tmp = root / f"LEDGER.csv.tmp.{watermark}"
    tmp.write_text(body, encoding="utf-8")
    tmp.replace(target)
    (root / "LEDGER.export.manifest.json").write_text(
        json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return {
        "ok": True,
        "manifest": manifest,
        "applied": True,
        "backup": str(backup) if backup.is_file() else "",
    }
