"""Google Drive share-link normalization and probe (COI Content Intake M1)."""

from __future__ import annotations

import re
from typing import Optional
from urllib.parse import parse_qs, urlparse

import httpx

GDRIVE_FILE_PATTERNS = (
    re.compile(r"drive\.google\.com/file/d/([a-zA-Z0-9_-]+)"),
    re.compile(r"drive\.google\.com/open\?[^#]*id=([a-zA-Z0-9_-]+)"),
    re.compile(r"drive\.google\.com/uc\?(?:[^#]*&)?id=([a-zA-Z0-9_-]+)"),
)

GDRIVE_FOLDER_PATTERNS = (
    re.compile(r"drive\.google\.com/drive/folders/([a-zA-Z0-9_-]+)"),
    re.compile(r"drive\.google\.com/drive/u/\d+/folders/([a-zA-Z0-9_-]+)"),
)

ALLOWED_MEDIA_HOSTS = (
    "drive.google.com",
    "docs.google.com",
    "lh3.googleusercontent.com",
    "lh4.googleusercontent.com",
    "lh5.googleusercontent.com",
    "lh6.googleusercontent.com",
)


def parse_gdrive_file_id(url: str) -> Optional[str]:
    """Extract Google Drive file ID from common share URL formats."""
    text = (url or "").strip()
    if not text:
        return None
    for pattern in GDRIVE_FILE_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    parsed = urlparse(text)
    if "drive.google.com" in (parsed.netloc or ""):
        qs = parse_qs(parsed.query)
        ids = qs.get("id") or []
        if ids:
            return ids[0]
    return None


def parse_gdrive_folder_id(url: str) -> Optional[str]:
    """Extract Google Drive folder ID from folder share URL."""
    text = (url or "").strip()
    if not text:
        return None
    for pattern in GDRIVE_FOLDER_PATTERNS:
        match = pattern.search(text)
        if match:
            return match.group(1)
    return None


def build_direct_download_url(file_id: str) -> str:
    """Canonical direct URL for Meta / probe (Approach 2)."""
    return f"https://drive.google.com/uc?export=download&id={file_id}"


def build_folder_url(folder_id: str) -> str:
    return f"https://drive.google.com/drive/folders/{folder_id}"


def normalize_media_url(url: str) -> dict:
    """
    Normalize pasted media URL. Returns dict with keys:
    ok, media_url, media_source, gdrive_file_id, error (PL message).
    """
    raw = (url or "").strip()
    if not raw:
        return {"ok": False, "error": "Brak linku do media"}

    file_id = parse_gdrive_file_id(raw)
    if file_id:
        return {
            "ok": True,
            "media_url": build_direct_download_url(file_id),
            "media_source": "gdrive",
            "gdrive_file_id": file_id,
            "original_url": raw,
        }

    parsed = urlparse(raw)
    host = (parsed.netloc or "").lower()
    if host and any(host == h or host.endswith("." + h) for h in ALLOWED_MEDIA_HOSTS):
        if raw.startswith("https://"):
            return {
                "ok": True,
                "media_url": raw,
                "media_source": "external",
                "gdrive_file_id": None,
                "original_url": raw,
            }

    return {
        "ok": False,
        "error": "Nie rozpoznano linku Google Drive — użyj linku Udostępnij z pliku",
    }


def probe_media_url(url: str, timeout: float = 12.0) -> dict:
    """
    HEAD/GET probe for publish-time availability.
    Returns ok, mime_type, status_code, error.
    """
    normalized = normalize_media_url(url)
    if not normalized.get("ok"):
        return {"ok": False, "error": normalized.get("error", "invalid url")}

    target = normalized["media_url"]
    try:
        with httpx.Client(follow_redirects=True, timeout=timeout) as client:
            resp = client.head(target)
            if resp.status_code >= 400:
                resp = client.get(target, headers={"Range": "bytes=0-0"})
            mime = (resp.headers.get("content-type") or "").split(";")[0].strip()
            ok = resp.status_code < 400 and bool(mime)
            return {
                "ok": ok,
                "mime_type": mime or None,
                "status_code": resp.status_code,
                "media_url": target,
                "media_source": normalized.get("media_source"),
                "gdrive_file_id": normalized.get("gdrive_file_id"),
                "error": None if ok else "Plik niedostępny — sprawdź udostępnianie (każdy z linkiem)",
            }
    except httpx.HTTPError as exc:
        return {"ok": False, "error": f"Probe failed: {exc}", "media_url": target}
