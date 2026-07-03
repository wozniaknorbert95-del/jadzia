"""Cost tracking and estimation endpoints."""

from fastapi import APIRouter, Depends

from api.dependencies import get_claude_service, verify_jwt
from core.models import CostEstimateRequest, CostEstimateResponse
from core.services import ClaudeService

router = APIRouter(tags=["costs"])


@router.get("/costs")
async def get_costs(
    claude: ClaudeService = Depends(get_claude_service),
    _auth=Depends(verify_jwt),
):
    """Get current cost statistics."""
    stats = claude.get_cost_stats()
    return {
        "input_tokens": stats.input_tokens,
        "output_tokens": stats.output_tokens,
        "cached_tokens": stats.cached_tokens,
        "total_cost": round(stats.total_cost, 6),
    }


@router.post("/costs/reset")
async def reset_costs(
    claude: ClaudeService = Depends(get_claude_service),
    _auth=Depends(verify_jwt),
):
    """Reset cost statistics."""
    claude.reset_cost_stats()
    return {"status": "ok", "message": "Cost stats reset"}


@router.post("/costs/estimate", response_model=CostEstimateResponse)
async def estimate_cost(request: CostEstimateRequest):
    """Estimate cost for a given message."""
    import tiktoken

    enc = tiktoken.encoding_for_model("gpt-4")
    input_tokens = len(enc.encode(request.message))
    output_tokens = input_tokens // 2
    cost = (input_tokens * 3 + output_tokens * 15) / 1_000_000
    return CostEstimateResponse(
        estimated_input_tokens=input_tokens,
        estimated_output_tokens=output_tokens,
        estimated_cost=round(cost, 6),
        model="claude-haiku-4-5-20251001",
    )
