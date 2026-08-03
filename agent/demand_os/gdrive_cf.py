"""GDrive / Content Factory asset list — OS §E MCP (honest modes).

Modes:
- local_registry: ASSET-REGISTRY.csv (always available, no network)
- stub: LIVE requested but not configured
- live: LIVE+creds — Drive v3 files.list via service account (google-auth + httpx)
- live_error: LIVE attempted but creds/transport failed (fail-closed + fallback)
Never return fake ok+empty as success. Zero network in CI: live path requires
DEMAND_OS_GDRIVE_LIVE=1 and tests inject the transport.
"""

from __future__ import annotations

import csv
import json
import os
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_REGISTRY = _REPO / "docs/ops/demand-os/set-now/ASSET-REGISTRY.csv"

_DRIVE_SCOPE = "https://www.googleapis.com/auth/drive.readonly"
_DRIVE_FILES_URL = "https://www.googleapis.com/drive/v3/files"


def gdrive_configured() -> bool:
    return bool(
        os.getenv("GDRIVE_FOLDER_ID")
        and (
            os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
            or os.getenv("GA4_CREDENTIALS_JSON")
            or os.getenv("GDRIVE_CREDENTIALS_JSON")
        )
    )


def _service_account_credentials():
    """Build SA credentials from inline JSON or file path. None when unusable."""
    from google.oauth2 import service_account

    inline = os.getenv("GDRIVE_CREDENTIALS_JSON", "").strip() or os.getenv(
        "GA4_CREDENTIALS_JSON", ""
    ).strip()
    if inline.startswith("{"):
        info = json.loads(inline)  # ValueError → caller maps to live_error
        return service_account.Credentials.from_service_account_info(
            info, scopes=[_DRIVE_SCOPE]
        )
    path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "").strip()
    if path and Path(path).is_file():
        return service_account.Credentials.from_service_account_file(
            path, scopes=[_DRIVE_SCOPE]
        )
    return None


def _bearer_token(creds: Any) -> str:
    from google.auth.transport.requests import Request

    creds.refresh(Request())
    return creds.token


def _default_http_get(url: str, *, headers: Dict[str, str], params: Dict[str, Any], timeout: float):
    import httpx

    return httpx.get(url, headers=headers, params=params, timeout=timeout)


def list_drive_folder(
    folder_id: str,
    *,
    limit: int = 20,
    token: Optional[str] = None,
    http_get: Optional[Callable[..., Any]] = None,
) -> Dict[str, Any]:
    """Drive v3 files.list for one folder — injectable transport, never raises."""
    try:
        if token is None:
            creds = _service_account_credentials()
            if creds is None:
                return {
                    "ok": False,
                    "mode": "missing_config",
                    "files": [],
                    "error": "no usable service account credentials",
                }
            token = _bearer_token(creds)
        get = http_get or _default_http_get
        resp = get(
            _DRIVE_FILES_URL,
            headers={"Authorization": f"Bearer {token}"},
            params={
                "q": f"'{folder_id}' in parents and trashed = false",
                "pageSize": max(1, min(int(limit), 100)),
                "fields": "files(id,name,mimeType,modifiedTime)",
                "orderBy": "modifiedTime desc",
            },
            timeout=15.0,
        )
        if resp.status_code != 200:
            return {
                "ok": False,
                "mode": "live_error",
                "files": [],
                "error": f"drive api http {resp.status_code}",
            }
        payload = resp.json()
        files = [
            {
                "gdrive_file_id": f.get("id") or "",
                "name": f.get("name") or "",
                "mime_type": f.get("mimeType") or "",
                "modified": f.get("modifiedTime") or "",
            }
            for f in payload.get("files", [])
        ]
        return {"ok": True, "mode": "live", "files": files, "error": ""}
    except Exception as exc:  # noqa: BLE001 — connector must fail closed
        return {
            "ok": False,
            "mode": "live_error",
            "files": [],
            "error": f"{type(exc).__name__}: {str(exc)[:240]}",
        }


def list_local_registry(*, limit: int = 20, path: Optional[Path] = None) -> Dict[str, Any]:
    src = path or DEFAULT_REGISTRY
    if not src.is_file():
        return {
            "ok": False,
            "mode": "missing_registry",
            "assets": [],
            "error": f"missing {src.name}",
        }
    with src.open(encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    assets: List[Dict[str, str]] = []
    for r in rows[: max(1, limit)]:
        assets.append(
            {
                "asset_id": r.get("asset_id") or "",
                "channel": r.get("channel") or "",
                "icp_role": r.get("icp_role") or "",
                "status": r.get("status") or "",
                "source": "ASSET-REGISTRY.csv",
            }
        )
    return {
        "ok": True,
        "mode": "local_registry",
        "assets": assets,
        "error": "",
        "limit": limit,
        "notes": "CF inventory from set-now registry — GDrive folder API separate",
    }


def list_cf_assets(*, limit: int = 5) -> Dict[str, Any]:
    """
    Default: local registry (honest CF list).
    DEMAND_OS_GDRIVE_LIVE=1 → attempt remote; if API missing → not_wired (ok=False).
    """
    if os.getenv("DEMAND_OS_GDRIVE_LIVE") != "1":
        return list_local_registry(limit=limit)

    if not gdrive_configured():
        return {
            "ok": False,
            "mode": "stub",
            "assets": [],
            "error": "DEMAND_OS_GDRIVE_LIVE=1 but missing GDRIVE_FOLDER_ID/creds",
            "limit": limit,
            "fallback": list_local_registry(limit=limit),
        }

    live = list_drive_folder(os.environ["GDRIVE_FOLDER_ID"], limit=limit)
    if not live["ok"]:
        return {
            "ok": False,
            "mode": live["mode"],
            "assets": [],
            "error": live["error"],
            "limit": limit,
            "fallback": list_local_registry(limit=limit),
            "notes": "OS §E MCP GDrive live failed closed — local registry is the floor",
        }
    assets = [
        {
            "asset_id": Path(f["name"]).stem if f["name"] else "",
            "channel": "",
            "icp_role": "",
            "status": "drive_file",
            "source": "gdrive_live",
            "gdrive_file_id": f["gdrive_file_id"],
            "mime_type": f["mime_type"],
            "modified": f["modified"],
        }
        for f in live["files"]
    ]
    return {
        "ok": True,
        "mode": "live",
        "assets": assets,
        "error": "",
        "limit": limit,
        "notes": "Drive v3 files.list — channel/icp come from ASSET-REGISTRY, not Drive",
    }


def list_cf_assets_stub(*, limit: int = 5) -> Dict[str, Any]:
    """Backward-compatible alias → list_cf_assets."""
    return list_cf_assets(limit=limit)
