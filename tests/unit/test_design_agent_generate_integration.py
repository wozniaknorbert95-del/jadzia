"""F-056: generate route propagates inspirationOnly ValueError as 400."""

from __future__ import annotations

from io import BytesIO
from pathlib import Path
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.app import create_app

_TIER_MATRIX = (
    Path(__file__).resolve().parents[3] / "flexgrafik-inspire" / "brain" / "tier-matrix.json"
)

pytestmark = pytest.mark.skipif(
    not _TIER_MATRIX.is_file(),
    reason="flexgrafik-inspire tier matrix not available",
)


@pytest.fixture(autouse=True)
def _tier_matrix_env(monkeypatch: pytest.MonkeyPatch) -> None:
    if _TIER_MATRIX.is_file():
        monkeypatch.setenv("DA_TIER_MATRIX_PATH", str(_TIER_MATRIX))


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
                "mockup_b_sku": "MA-005",
                "mockup_a_sku": "CS-SET-PRO-ZZP",
                "budget_range": "300_600",
                "budget_explicit": "true",
            },
            files={"logo": ("logo.png", _logo_png(), "image/png")},
        )
    assert resp.status_code == 400
    detail = resp.json()["detail"]
    assert detail["error_code"] == "GENERATION_FAILED"
    assert "Brief incomplete" in detail["message"]


def test_generate_resolves_empty_sku(client: TestClient) -> None:
    from agent.inspire.engine import InspireResponse, MockupResult

    fake = InspireResponse(
        brief_id="test-brief",
        mockups=[
            MockupResult(variant="tier_b", panel="deur", url="https://x/mock_b.png", sku="MA-005"),
            MockupResult(variant="tier_a", panel="deur", url="https://x/mock_a.png", sku="CS-SET-PRO-ZZP"),
        ],
        recommended_products=[],
        wizard_deeplink="https://zzpackage.flexgrafik.nl/wizard",
        cost_eur=0.1,
        positionering="balanced",
        user_stijl="balanced",
        mockup_b_sku="MA-005",
        mockup_a_sku="CS-SET-PRO-ZZP",
        engine_mode="inspirationOnly",
        generator_provider="stub",
    )
    with patch(
        "agent.inspire.engine.generate_inspire_mockups",
        return_value=fake,
    ) as mock_gen:
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
                "mockup_b_sku": "",
                "mockup_a_sku": "",
                "budget_range": "300_600",
                "budget_explicit": "true",
            },
            files={"logo": ("logo.png", _logo_png(), "image/png")},
        )
    assert resp.status_code == 200
    assert mock_gen.call_args.kwargs["mockup_b_sku"]
    assert mock_gen.call_args.kwargs["mockup_a_sku"]
