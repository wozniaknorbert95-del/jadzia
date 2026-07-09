#!/usr/bin/env python3
"""Save COI-Marketing Google Drive folder link in Commander settings.

Usage (VPS or local with PYTHONPATH=repo root):
  python3 deployment/set-marketing-gdrive-folder.py "https://drive.google.com/drive/folders/XXXX"
"""
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(_root))

from agent.commander.settings import update_settings
from agent.media.gdrive import build_folder_url, parse_gdrive_folder_id

folder_url = sys.argv[1] if len(sys.argv) > 1 else ""
if not folder_url:
    print("usage: set-marketing-gdrive-folder.py <folder_share_url>", file=sys.stderr)
    sys.exit(1)

folder_id = parse_gdrive_folder_id(folder_url)
if not folder_id:
    print("error: not a Google Drive folder URL", file=sys.stderr)
    sys.exit(1)

canonical = build_folder_url(folder_id)
result = update_settings({
    "marketing_gdrive_folder_url": canonical,
    "marketing_gdrive_folder_id": folder_id,
})
print(json.dumps({
    "marketing_gdrive_folder_url": result.get("marketing_gdrive_folder_url"),
    "marketing_gdrive_folder_id": result.get("marketing_gdrive_folder_id"),
}, indent=2))
