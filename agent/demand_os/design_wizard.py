"""Design Agent dual-cash guard — OS B.7 (mockup → Wizard deeplink)."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional

from agent.demand_os.utm_lock import build_wizard_utm, validate_utm_url

_OFFERTE_RE = re.compile(r"\b(offerte|quote|prijsopgave)\b", re.IGNORECASE)
_MOCKUP_RE = re.compile(r"\b(mockup|ontwerp|design|preview)\b", re.IGNORECASE)


def check_design_lead(
    *,
    message: str,
    wizard_url: str = "",
    lead_id: str = "design_lead",
    hours_since_mockup: Optional[float] = None,
) -> Dict[str, Any]:
    """
    PASS if Wizard deeplink present and valid.
    FAIL if offerte-only / mockup without Wizard / >24h without link.
    """
    body = (message or "").strip()
    fails = []
    url = (wizard_url or "").strip()
    if not url:
        # try extract from message
        m = re.search(r"https?://\S+", body)
        url = m.group(0) if m else ""

    has_mockup = bool(_MOCKUP_RE.search(body))
    has_offerte = bool(_OFFERTE_RE.search(body))
    utm = validate_utm_url(url) if url else {"ok": False}

    if has_offerte and not utm.get("ok"):
        fails.append("offerte_without_wizard")
    if has_mockup and not utm.get("ok"):
        fails.append("mockup_without_wizard")
    if hours_since_mockup is not None and hours_since_mockup > 24 and not utm.get("ok"):
        fails.append("wizard_deeplink_gt_24h")
    if not url and not has_mockup and not has_offerte:
        # neutral note — suggest template
        pass

    suggested = build_wizard_utm("design_agent", "installateur", f"da_{lead_id}")
    return {
        "ok": len(fails) == 0 and bool(utm.get("ok") or not (has_mockup or has_offerte)),
        "fails": fails,
        "utm_ok": bool(utm.get("ok")),
        "wizard_url": url or suggested,
        "suggested_wizard": suggested,
        "rule": "mockup→Wizard <24h · offerte ≠ success",
        "marketing": "PARKED_LAST",
    }
