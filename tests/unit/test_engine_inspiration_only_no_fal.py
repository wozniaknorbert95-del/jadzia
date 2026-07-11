"""F-044: inspirationOnly mode must not fall back to fal."""

from __future__ import annotations

import os
from unittest.mock import patch

import pytest

from agent.inspire import engine as inspire_engine


def test_inspiration_failure_raises_no_fal_fallback(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("INSPIRE_RENDER_MODE", "inspirationOnly")
    monkeypatch.delenv("FAL_KEY", raising=False)

    with patch.object(inspire_engine, "_try_inspiration_generate", return_value=None):
        with pytest.raises(ValueError, match="Inspiration pipeline unavailable"):
            inspire_engine.generate_inspire_mockups(
                vehicle="caddy",
                branche="IT",
                bedrijfsnaam="Test",
                telefoon="",
                website="",
                brand_colors=["#333"],
                tekst_opties=[],
                slogan="",
                logo_bytes=b"\x89PNG",
                output_dir=inspire_engine.Path("/tmp"),
                ssot_path=inspire_engine.Path("/tmp/ssot.json"),
            )
