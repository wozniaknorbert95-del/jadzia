"""Design Agent offerte concierge endpoint."""

from __future__ import annotations

from fastapi import APIRouter, Header, HTTPException, Request, Response

from agent.design_agent_service import _verify_api_key
from agent.inspire.chat_locale import error_message, normalize_locale
from agent.inspire.offerte_service import create_offerte_request
from core.models import DesignAgentOfferteRequest, DesignAgentOfferteResponse

router = APIRouter(tags=["design-agent"])

_NO_CACHE_HEADERS = {
    "Cache-Control": "no-store, no-cache, must-revalidate, max-age=0",
    "Pragma": "no-cache",
}


def _apply_no_cache(response: Response) -> None:
    for key, value in _NO_CACHE_HEADERS.items():
        response.headers[key] = value


@router.post(
    "/api/v1/design-agent/offerte-request",
    response_model=DesignAgentOfferteResponse,
    status_code=201,
)
async def design_agent_offerte_request(
    request: Request,
    response: Response,
    request_body: DesignAgentOfferteRequest,
    x_fg_design_agent_key: str | None = Header(None, alias="X-FG-Design-Agent-Key"),
) -> DesignAgentOfferteResponse:
    _verify_api_key(x_fg_design_agent_key)
    client_ip = request.client.host if request.client else "unknown"
    loc = normalize_locale(request_body.locale)
    try:
        result = create_offerte_request(
            request_body.model_dump(exclude_none=True),
            client_ip=client_ip,
        )
    except ValueError as exc:
        code = str(exc)
        if code == "rate_limit":
            raise HTTPException(
                status_code=429,
                detail=error_message("rate_limit_offerte", loc) or "Te veel offerte-aanvragen.",
            ) from exc
        raise HTTPException(status_code=400, detail=code) from exc

    _apply_no_cache(response)
    status = 201
    if result.get("duplicate"):
        status = 200
    response.status_code = status
    return DesignAgentOfferteResponse(
        ok=True,
        offerte_request_id=result["offerte_request_id"],
        message_nl=result.get("message_nl") or "Bedankt — je offerte-aanvraag is ontvangen.",
        notify_team=result.get("notify_team"),
        notify_client=result.get("notify_client"),
    )
