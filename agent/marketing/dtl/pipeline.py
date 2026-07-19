"""DTL ingest orchestrator — called by worker scheduled hook."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List

logger = logging.getLogger(__name__)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def run_dtl_ingest(
    *,
    include_ga4: bool = True,
    include_l0: bool = True,
    period_days: int = 7,
) -> Dict[str, Any]:
    """
    Run full F0 ingest pipeline into SQLite DTL tables.
    Each step is isolated — one failure does not abort the rest.
    """
    from agent.marketing.dtl.attribution import ingest_attribution
    from agent.marketing.dtl.facebook_organic import ingest_facebook_organic_posts
    from agent.marketing.dtl.ga4 import ingest_ga4_snapshot
    from agent.marketing.dtl.l0_probe import ingest_l0_pixel_probe
    from agent.marketing.dtl.margin import ingest_order_margins
    from agent.marketing.dtl.ops import ingest_leads_snapshot, ingest_orders_snapshot
    from agent.marketing.dtl.quality import run_quality_pass

    started = _utc_now()
    steps: List[Dict[str, Any]] = []

    def _safe(name: str, fn) -> None:
        try:
            result = fn()
            steps.append(result if isinstance(result, dict) else {"source": name, "status": "ok"})
        except Exception as exc:
            logger.error("[dtl.pipeline] step=%s failed: %s", name, exc, exc_info=True)
            steps.append({"source": name, "status": "error", "error": str(exc)})

    if include_ga4:
        _safe("ga4", lambda: ingest_ga4_snapshot(period_days=period_days))
    _safe("orders", ingest_orders_snapshot)
    _safe("leads", ingest_leads_snapshot)
    if include_l0:
        _safe("l0_pixel", ingest_l0_pixel_probe)
    _safe("margin", ingest_order_margins)
    _safe("attribution", ingest_attribution)
    _safe("facebook_organic", ingest_facebook_organic_posts)

    quality: Dict[str, Any] = {}
    try:
        quality = run_quality_pass()
    except Exception as exc:
        logger.error("[dtl.pipeline] quality pass failed: %s", exc, exc_info=True)
        quality = {"status": "error", "error": str(exc)}

    ok = sum(1 for s in steps if s.get("status") in ("ok", "degraded"))
    errors = sum(1 for s in steps if s.get("status") == "error")
    summary = {
        "started_at": started,
        "finished_at": _utc_now(),
        "steps_ok": ok,
        "steps_error": errors,
        "steps": steps,
        "quality": quality,
    }
    logger.info(
        "[dtl.pipeline] done ok=%s err=%s",
        ok,
        errors,
    )
    return summary
