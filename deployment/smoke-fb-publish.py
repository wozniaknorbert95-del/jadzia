#!/usr/bin/env python3
"""Smoke: text + photo publish after token rotation (no secrets printed)."""
from __future__ import annotations

import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import jwt

ROOT = Path(__file__).resolve().parent.parent
ENV = ROOT / ".env"
BASE = "http://localhost:8000"
IMAGE_URL = "https://drive.google.com/file/d/1CviVVE_KDdK1r3mw8ftx5SLW5WT7oo54/view"


def load_env() -> dict[str, str]:
    out: dict[str, str] = {}
    for line in ENV.read_text(encoding="utf-8", errors="replace").splitlines():
        if "=" in line and not line.strip().startswith("#"):
            k, _, v = line.partition("=")
            out[k.strip()] = v.strip().strip('"').strip("'")
    return out


def curl_json(method: str, path: str, token: str, data: dict | None = None) -> tuple[int, dict]:
    cmd = [
        "curl", "-sS", "-w", "\n%{http_code}", "-X", method,
        "-H", f"Authorization: Bearer {token}",
        "-H", "Content-Type: application/json",
        f"{BASE}{path}",
    ]
    if data is not None:
        cmd.extend(["-d", json.dumps(data)])
    out = subprocess.check_output(cmd, text=True)
    body, _, code = out.rpartition("\n")
    try:
        parsed = json.loads(body) if body.strip() else {}
    except json.JSONDecodeError:
        parsed = {"raw": body[:400]}
    return int(code), parsed


def main() -> int:
    env = load_env()
    tok = jwt.encode({"sub": "fb-smoke", "role": "dowodca"}, env["JWT_SECRET"], algorithm="HS256")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    # Text publish
    code, created = curl_json(
        "POST",
        "/api/v1/content-calendar",
        tok,
        {
            "platform": "facebook",
            "title": f"FB token smoke text {ts}",
            "body_nl": f"Jadzia token smoke {ts} — safe to delete.",
            "scheduled_at": "2026-08-01T09:00:00Z",
            "content_type": "text",
            "status": "draft",
        },
    )
    print("TEXT_CREATE", code, created.get("sync_status"))
    if code != 200:
        return 1
    eid = str(created["entry_id"])
    curl_json("PATCH", f"/api/v1/content-calendar/{eid}", tok, {"status": "approved"})
    code, pub = curl_json("POST", f"/api/v1/content-calendar/{eid}/publish", tok, {})
    print("TEXT_PUBLISH", code, pub.get("status"), "post_id=" + str(pub.get("post_id") or pub.get("detail", {}).get("post_id") if isinstance(pub.get("detail"), dict) else ""))
    if code != 200 or pub.get("status") != "success":
        # publish route may wrap differently
        detail = pub.get("detail") if isinstance(pub.get("detail"), dict) else pub
        print("TEXT_DETAIL", json.dumps(detail, ensure_ascii=False)[:500])
        if not (isinstance(detail, dict) and detail.get("status") == "success"):
            return 1
        print("TEXT_PASS", detail.get("post_id"))
    else:
        print("TEXT_PASS", pub.get("post_id"))

    # Photo publish
    code, created = curl_json(
        "POST",
        "/api/v1/content-calendar",
        tok,
        {
            "platform": "facebook",
            "title": f"FB token smoke photo {ts}",
            "body_nl": f"Jadzia photo smoke {ts} — safe to delete.",
            "scheduled_at": "2026-08-01T09:00:00Z",
            "content_type": "image",
            "media_url": IMAGE_URL,
            "status": "draft",
        },
    )
    print("PHOTO_CREATE", code, created.get("sync_status") or created.get("detail"))
    if code != 200:
        return 1
    eid = str(created["entry_id"])
    curl_json("PATCH", f"/api/v1/content-calendar/{eid}", tok, {"status": "approved"})
    code, pub = curl_json("POST", f"/api/v1/content-calendar/{eid}/publish", tok, {})
    detail = pub if pub.get("status") else pub.get("detail", pub)
    print("PHOTO_PUBLISH", code, json.dumps(detail, ensure_ascii=False)[:400])
    if not (isinstance(detail, dict) and detail.get("status") == "success"):
        return 1
    print("PHOTO_PASS", detail.get("post_id"))
    print("FB_PUBLISH_SMOKE_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
