"""Design Agent API route tests (mocked service — no VGE on CI)."""

from __future__ import annotations

from io import BytesIO
from unittest.mock import AsyncMock, patch

import pytest
from fastapi.testclient import TestClient
from PIL import Image

from api.app import create_app
from core.models import DesignAgentGenerateResponse, DesignAgentMockupItem, DesignAgentProductItem


def _logo_png() -> bytes:
    buf = BytesIO()
    Image.new("RGBA", (64, 64), (0, 63, 135, 255)).save(buf, format="PNG")
    return buf.getvalue()


@pytest.fixture
def client():
    return TestClient(create_app())


def test_design_agent_route_registered(client: TestClient) -> None:
    openapi = client.get("/openapi.json")
    assert openapi.status_code == 200
    paths = set(openapi.json().get("paths", {}).keys())
    assert "/api/v1/design-agent/generate" in paths


@patch("api.routes.design_agent.process_design_agent_generate", new_callable=AsyncMock)
def test_design_agent_generate_200_mocked(mock_proc: AsyncMock, client: TestClient) -> None:
    mock_proc.return_value = DesignAgentGenerateResponse(
        brief_id="test-brief-id",
        mockups=[
            DesignAgentMockupItem(
                variant="tier_b",
                panel="deur",
                url="https://api.zzpackage.flexgrafik.nl/uploads/design-agent/test/mockup_tier_b.png",
                sku="MA-005",
                naam="Magneten set Caddy",
                price_suggested=129.0,
                label_nl="Smart Start",
            ),
            DesignAgentMockupItem(
                variant="tier_a",
                panel="deur",
                url="https://api.zzpackage.flexgrafik.nl/uploads/design-agent/test/mockup_tier_a.png",
                sku="CS-SET-PRO-ZZP",
                naam="Pro ZZP set Caddy",
                price_suggested=199.0,
                label_nl="Premium Presence",
            ),
        ],
        recommended_products=[
            DesignAgentProductItem(sku="MA-005", naam="Magneten", price_suggested=129.0, highlight=True),
            DesignAgentProductItem(sku="CS-SET-PRO-ZZP", naam="Pro ZZP", price_suggested=199.0, highlight=True),
            DesignAgentProductItem(sku="DF-004", naam="DTP", price_suggested=199.0, highlight=False),
        ],
        wizard_deeplink="https://zzpackage.flexgrafik.nl/wizard/?voertuig=caddy&highlight=MA-005",
        cost_eur=0.22,
        positionering="strak",
        mockup_b_sku="MA-005",
        mockup_a_sku="CS-SET-PRO-ZZP",
        user_stijl="strak",
    )

    resp = client.post(
        "/api/v1/design-agent/generate",
        data={
            "vehicle": "caddy",
            "bedrijfsnaam": "Test BV",
            "branche": "Elektricien",
            "diensten": "Storingen, groepenkast",
            "doelgroep": "Particulieren",
            "positionering": "strak",
            "brief_confirmed": "true",
        },
        files={"logo": ("logo.png", _logo_png(), "image/png")},
    )

    assert resp.status_code == 200
    body = resp.json()
    assert len(body["mockups"]) == 2
    assert body["mockups"][0]["variant"] == "tier_b"
    assert body["mockups"][0]["sku"] == "MA-005"
    assert body["mockups"][0]["label_nl"] == "Smart Start"
    assert body["positionering"] == "strak"
    assert body["mockup_b_sku"] == "MA-005"


def test_design_agent_generate_400_brief_not_confirmed(client: TestClient) -> None:
    resp = client.post(
        "/api/v1/design-agent/generate",
        data={
            "vehicle": "caddy",
            "bedrijfsnaam": "Test BV",
            "branche": "Elektricien",
            "brief_confirmed": "false",
        },
        files={"logo": ("logo.png", _logo_png(), "image/png")},
    )
    assert resp.status_code == 400
    assert "Bevestig je briefing eerst" in resp.json()["detail"]


def test_design_agent_generate_401_without_key(client: TestClient) -> None:
    with patch.dict("os.environ", {"FG_DESIGN_AGENT_KEY": "test-secret"}, clear=False):
        app = create_app()
        c = TestClient(app)
        resp = c.post(
            "/api/v1/design-agent/generate",
            data={
                "vehicle": "caddy",
                "bedrijfsnaam": "Test BV",
                "stijl": "strak",
                "brief_confirmed": "true",
            },
            files={"logo": ("logo.png", _logo_png(), "image/png")},
        )
    assert resp.status_code == 401
