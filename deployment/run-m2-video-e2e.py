#!/usr/bin/env python3
"""M2 prod E2E: MIME gate + Graph video publish (short public MP4).

Run on VPS: python3 deployment/run-m2-video-e2e.py
Does not print secrets.
"""

from __future__ import annotations

import json
import os
import sqlite3
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

import jwt

ROOT = Path(__file__).resolve().parent.parent
ENV_FILE = Path(os.environ.get("JADZIA_ENV_FILE", str(ROOT / ".env")))
BASE = os.environ.get("JADZIA_BASE_URL", "http://localhost:8000")
DB_PATH = Path(os.environ.get("JADZIA_DB_PATH", str(ROOT / "data" / "jadzia.db")))

# Short public MP4 Meta can fetch (GDrive MP4 optional via M2_TEST_GDRIVE_URL).
DEFAULT_VIDEO_URL = (
    "https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4"
)
# Known published Marketing image on Drive — used to assert video MIME gate.
IMAGE_DRIVE_URL = "https://drive.google.com/file/d/1CviVVE_KDdK1r3mw8ftx5SLW5WT7oo54/view"


def load_env(path: Path) -> dict[str, str]:
    env: dict[str, str] = {}
    for line in path.read_text(encoding="utf-8", errors="replace").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, val = line.partition("=")
        env[key.strip()] = val.strip().strip('"').strip("'")
    return env


def curl_json(method: str, path: str, token: str, data: dict | None = None) -> tuple[int, dict]:
    cmd = [
        "curl",
        "-sS",
        "-w",
        "\n%{http_code}",
        "-X",
        method,
        "-H",
        f"Authorization: Bearer {token}",
        "-H",
        "Content-Type: application/json",
        f"{BASE}{path}",
    ]
    if data is not None:
        cmd.extend(["-d", json.dumps(data)])
    out = subprocess.check_output(cmd, text=True)
    body, _, code = out.rpartition("\n")
    parsed: dict
    try:
        parsed = json.loads(body) if body.strip() else {}
    except json.JSONDecodeError:
        parsed = {"raw": body[:500]}
    return int(code), parsed


def main() -> int:
    if not ENV_FILE.is_file():
        print(f"FAIL: missing {ENV_FILE}")
        return 1

    env = load_env(ENV_FILE)
    secret = env.get("JWT_SECRET")
    if not secret:
        print("FAIL: JWT_SECRET missing")
        return 1
    if not env.get("FB_PAGE_ID") or not env.get("FB_ACCESS_TOKEN"):
        print("FAIL: FB_PAGE_ID / FB_ACCESS_TOKEN missing")
        return 1

    token = jwt.encode({"sub": "m2-e2e", "role": "dowodca"}, secret, algorithm="HS256")
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")

    print("=== M2 E2E A: video MIME gate (image Drive URL must 400) ===")
    code, body = curl_json(
        "POST",
        "/api/v1/content-calendar",
        token,
        {
            "platform": "facebook",
            "title": f"M2 mime gate {ts}",
            "body_nl": "should fail",
            "scheduled_at": "2026-08-01T09:00:00Z",
            "content_type": "video",
            "media_url": IMAGE_DRIVE_URL,
            "status": "draft",
        },
    )
    print("MIME_GATE_HTTP", code)
    print("MIME_GATE_BODY", json.dumps(body, ensure_ascii=False)[:400])
    if code != 400:
        print("FAIL: expected HTTP 400 for image-as-video")
        return 1

    video_url = os.environ.get("M2_TEST_GDRIVE_URL") or DEFAULT_VIDEO_URL
    print("=== M2 E2E B: Graph video publish ===")
    print("VIDEO_URL_HOST", video_url.split("/")[2] if "://" in video_url else "unknown")

    # Prefer API create when URL is GDrive (probe path). Else insert approved row for Graph-only proof.
    entry_id: str
    if "drive.google.com" in video_url:
        code, created = curl_json(
            "POST",
            "/api/v1/content-calendar",
            token,
            {
                "platform": "facebook",
                "title": f"M2 video E2E {ts}",
                "body_nl": f"Jadzia M2 video test {ts} — safe to delete.",
                "scheduled_at": "2026-08-01T09:00:00Z",
                "scheduled_publish_at": "2026-08-01T09:00:00Z",
                "content_type": "video",
                "media_url": video_url,
                "status": "draft",
            },
        )
        print("CREATE_HTTP", code, json.dumps(created, ensure_ascii=False)[:400])
        if code != 200 or created.get("sync_status") != "success":
            print("FAIL: create video entry")
            return 1
        entry_id = str(created["entry_id"])
        code, patched = curl_json(
            "PATCH",
            f"/api/v1/content-calendar/{entry_id}",
            token,
            {"status": "approved"},
        )
        print("PATCH_HTTP", code, json.dumps(patched, ensure_ascii=False)[:300])
        if code != 200:
            print("FAIL: approve")
            return 1
    else:
        now = datetime.now(timezone.utc).isoformat()
        conn = sqlite3.connect(str(DB_PATH))
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO content_calendar (
              platform, title, body_nl, scheduled_at, status,
              content_type, media_url, media_source, scheduled_publish_at,
              created_at, updated_at, version
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                "facebook",
                f"M2 video E2E {ts}",
                f"Jadzia M2 video test {ts} — safe to delete.",
                "2020-01-01T10:00:00+00:00",
                "approved",
                "video",
                video_url,
                "external",
                "2020-01-01T10:00:00+00:00",
                now,
                now,
                1,
            ),
        )
        conn.commit()
        entry_id = str(cur.lastrowid)
        conn.close()
        print("CREATED_ENTRY_DB", entry_id)

    code, pub = curl_json("POST", f"/api/v1/content-calendar/{entry_id}/publish", token, {})
    print("PUBLISH_HTTP", code)
    print("PUBLISH_BODY", json.dumps(pub, ensure_ascii=False)[:800])
    if code != 200 or pub.get("status") != "success" or not pub.get("post_id"):
        print("FAIL: publish video")
        return 1

    code, status = curl_json("GET", f"/api/v1/content-calendar/{entry_id}/publish-status", token)
    print("STATUS_HTTP", code)
    print("STATUS_BODY", json.dumps(status, ensure_ascii=False)[:800])
    if status.get("status") != "published" or not status.get("fb_post_id"):
        print("FAIL: publish-status")
        return 1

    print(
        f"=== M2_E2E_PASS === entry_id={entry_id} fb_post_id={pub['post_id']} "
        f"content_type=video"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
