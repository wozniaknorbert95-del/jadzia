"""F-056: generate route propagates inspirationOnly ValueError as 400."""

from __future__ import annotations

from io import BytesIO
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.app import create_app


def _logo_png() -> bytes:
    buf = BytesIO()
    Image.new("RGBA", (64, 64), (0, 63, 135, 255)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def client():
    return TestClient(create_app())


def test_generate_value_error_returns_400_not_503(client: TestClient) -> None:
    with patch(
        "agent.inspire.engine.generate_inspire_mockups",
        side_effect=ValueError("Brief incomplete: regio"),
    ):
        resp = client.post(
            "/api/v1/design-agent/generate",
            data={
                "vehicle": "caddy",
                "bedrijfsnaam": "Test BV",
                "branche": "Elektricien",
                "diensten": "Storingen",
                "doelgroep": "Particulieren",
                "positionering": "strak",
                "brief_confirmed": "true",
                "session_id": "integration-test",
            },
            files={"logo": ("logo.png", _logo_png(), "image/png")},
        )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["error_code"] == "GENERATION_FAILED"
    assert "Brief incomplete" in detail["message"]
