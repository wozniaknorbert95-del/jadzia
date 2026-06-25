"""Portal qualification endpoint — INT-012."""

from fastapi import APIRouter, HTTPException

from core.models import PortalQualifyRequest, PortalQualifyResponse

router = APIRouter(tags=["portal-qualification"])


@router.post("/api/v1/portal/qualify", response_model=PortalQualifyResponse)
async def portal_qualify(request: PortalQualifyRequest):
    """Structured qualification funnel for flexgrafik.nl (not customer_agent)."""
    try:
        from agent.portal_qualification_agent import process_portal_qualification

        result = await process_portal_qualification(
            session_id=request.session_id,
            message=request.message,
            step=request.step,
            consent_lead_storage=request.consent_lead_storage,
        )
        return PortalQualifyResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e)) from e
