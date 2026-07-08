"""fal.ai flux-pro/kontext full-frame client."""

from __future__ import annotations

import logging
import os
import tempfile
import urllib.request
from pathlib import Path

logger = logging.getLogger(__name__)

MODEL_ID = "fal-ai/flux-pro/kontext"
GUIDANCE = 3.5
STRENGTH = 0.55


def _read_key_file(path: Path) -> str:
    raw = path.read_text(encoding="utf-8-sig").strip()
    return raw.splitlines()[0].strip()


def _get_fal_key() -> str:
    key = os.getenv("FAL_KEY") or os.getenv("FAL_API_KEY", "")
    if not key:
        fal_local = os.getenv("FAL_KEY_LOCAL_PATH", "")
        if fal_local and Path(fal_local).is_file():
            key = _read_key_file(Path(fal_local))
    if not key:
        spike = Path(__file__).resolve().parents[3] / "zzpackage.flexgrafik.nl" / "docs" / "ops" / "spike-01" / ".fal-key.local"
        if spike.is_file():
            key = _read_key_file(spike)
    if not key:
        raise RuntimeError("FAL_KEY not configured")
    return key


def generate_mockup_png(
    ref_png: bytes,
    prompt: str,
    negative_prompt: str,
) -> bytes:
    import fal_client

    os.environ["FAL_KEY"] = _get_fal_key()
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as tmp:
        tmp.write(ref_png)
        tmp_path = tmp.name
    try:
        image_url = fal_client.upload_file(tmp_path)
        args = {
            "prompt": prompt,
            "image_url": image_url,
            "guidance_scale": GUIDANCE,
            "strength": STRENGTH,
            "num_images": 1,
            "output_format": "png",
        }
        if negative_prompt:
            args["negative_prompt"] = negative_prompt
        result = fal_client.subscribe(MODEL_ID, arguments=args, with_logs=False)
        images = result.get("images") or []
        if not images or not images[0].get("url"):
            raise RuntimeError("fal returned no image URL")
        url = images[0]["url"]
        with urllib.request.urlopen(url, timeout=120) as resp:
            return resp.read()
    finally:
        Path(tmp_path).unlink(missing_ok=True)
