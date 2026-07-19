"""L0 pixel HTML probe — presence of fbq / fbevents / GTM (not event fire proof)."""

from __future__ import annotations

import logging
import os
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from agent.db import (
    db_deactivate_quality_flags,
    db_insert_marketing_raw_ingest,
    db_insert_quality_flag,
    db_upsert_marketing_fact,
)
from agent.marketing.dtl.checksum import payload_checksum

logger = logging.getLogger(__name__)

DEFAULT_WIZARD_URL = "https://zzpackage.flexgrafik.nl/wizard/"
WINDOW = "live_probe"


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def probe_wizard_html(url: str, timeout: float = 10.0) -> Dict[str, Any]:
    """Fetch HTML and detect pixel/GTM markers. No Meta API calls."""
    req = urllib.request.Request(
        url,
        headers={"User-Agent": "jadzia-dtl-l0-probe/1.0"},
        method="GET",
    )
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        status = int(getattr(resp, "status", 200) or 200)
        body = resp.read().decode("utf-8", errors="replace")
    lower = body.lower()
    return {
        "url": url,
        "http_status": status,
        "fbq": "fbq(" in lower or "fbq =" in lower or "fbq=" in lower,
        "fbevents": "fbevents.js" in lower or "connect.facebook.net" in lower,
        "gtm": "googletagmanager.com/gtm.js" in lower or "gtm.start" in lower,
        "body_bytes": len(body.encode("utf-8", errors="replace")),
    }


def ingest_l0_pixel_probe(url: Optional[str] = None) -> Dict[str, Any]:
    """
    Probe Wizard HTML for pixel markers → raw + facts + quality flags.
    Note: HTML presence ≠ InitiateCheckout/Purchase fire (Events Manager = human).
    """
    as_of = _utc_now()
    source = "l0_pixel"
    target = (url or os.getenv("DTL_L0_PROBE_URL") or DEFAULT_WIZARD_URL).strip()

    try:
        result = probe_wizard_html(target)
        status = "ok"
        error_message = None
    except (urllib.error.URLError, TimeoutError, OSError) as exc:
        logger.warning("[dtl.l0] probe failed url=%s err=%s", target, exc)
        result = {
            "url": target,
            "http_status": None,
            "fbq": False,
            "fbevents": False,
            "gtm": False,
            "error": str(exc),
        }
        status = "error"
        error_message = str(exc)

    ingest_id = db_insert_marketing_raw_ingest(
        {
            "source": source,
            "fetched_at": as_of,
            "checksum": payload_checksum(result),
            "payload": result,
            "window_label": WINDOW,
            "status": status,
            "error_message": error_message,
        }
    )

    markers_ok = bool(result.get("fbq") and result.get("fbevents"))
    for metric_key, value in (
        ("l0_pixel_fbq", 1.0 if result.get("fbq") else 0.0),
        ("l0_pixel_fbevents", 1.0 if result.get("fbevents") else 0.0),
        ("l0_pixel_gtm", 1.0 if result.get("gtm") else 0.0),
        ("l0_pixel_html_ok", 1.0 if markers_ok else 0.0),
    ):
        db_upsert_marketing_fact(
            {
                "metric_key": metric_key,
                "channel": "meta",
                "window_label": WINDOW,
                "value": value,
                "confidence": 0.8 if status == "ok" else 0.0,
                "as_of": as_of,
                "source_ingest_id": ingest_id,
                "dims": {"url": target, "note": "html_probe_not_event_fire"},
            }
        )

    if status == "error":
        db_insert_quality_flag(
            {
                "flag_type": "api_error",
                "source": source,
                "severity": "red",
                "message": f"L0 HTML probe failed: {error_message}",
                "as_of": as_of,
                "details": result,
            }
        )
    elif not markers_ok:
        db_insert_quality_flag(
            {
                "flag_type": "missing",
                "source": source,
                "severity": "red",
                "message": "L0 pixel markers missing in Wizard HTML (fbq/fbevents)",
                "as_of": as_of,
                "details": result,
            }
        )
    else:
        db_deactivate_quality_flags(source, "api_error")
        db_deactivate_quality_flags(source, "missing")
        # Split IC vs Purchase — do not keep a single amber that blocks overall
        # after InitiateCheckout PASS + Purchase conscious PARK.
        db_deactivate_quality_flags(f"{source}_events", "missing")
        ic_verified = (os.getenv("L0_IC_VERIFIED") or "").strip().lower() in (
            "1",
            "true",
            "yes",
        )
        if ic_verified:
            db_insert_quality_flag(
                {
                    "flag_type": "ack",
                    "source": f"{source}_events_ic",
                    "severity": "info",
                    "message": (
                        "L0 InitiateCheckout VERIFIED (L0_IC_VERIFIED=1) — "
                        "HTML pixel OK"
                    ),
                    "as_of": as_of,
                    "details": {"url": target, "event": "InitiateCheckout"},
                }
            )
        else:
            db_insert_quality_flag(
                {
                    "flag_type": "missing",
                    "source": f"{source}_events_ic",
                    "severity": "amber",
                    "message": (
                        "HTML pixel OK — InitiateCheckout still needs Events "
                        "Manager verification (set L0_IC_VERIFIED=1 after PASS)"
                    ),
                    "as_of": as_of,
                    "details": {"url": target, "event": "InitiateCheckout"},
                }
            )
        # Purchase = conscious PARK (Mollie) — info only, never drives overall amber
        db_deactivate_quality_flags(f"{source}_events_purchase", "park")
        db_insert_quality_flag(
            {
                "flag_type": "park",
                "source": f"{source}_events_purchase",
                "severity": "info",
                "message": (
                    "L0 Purchase PARK (Mollie GO) — conscious; not a health failure"
                ),
                "as_of": as_of,
                "details": {"url": target, "event": "Purchase", "park": True},
            }
        )

    logger.info(
        "[dtl.l0] status=%s fbq=%s fbevents=%s gtm=%s",
        status,
        result.get("fbq"),
        result.get("fbevents"),
        result.get("gtm"),
    )
    return {
        "source": source,
        "status": status,
        "ingest_id": ingest_id,
        "markers_ok": markers_ok,
        "result": result,
        "as_of": as_of,
    }
