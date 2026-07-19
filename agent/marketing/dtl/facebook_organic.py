"""Facebook organic post metrics → DTL facts (HEU_ORGANIC_WINNER feed)."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from agent.db import (
    db_insert_marketing_raw_ingest,
    db_list_calendar_entries,
    db_upsert_marketing_fact,
)
from agent.marketing.dtl.checksum import payload_checksum

logger = logging.getLogger(__name__)

WINDOW = "vs_30d"
MIN_IMPRESSIONS_DEFAULT = 100


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _lift_pct(value: float, baseline: float) -> Optional[float]:
    if baseline is None or baseline <= 0:
        return None
    return 100.0 * (value - baseline) / baseline


def ingest_facebook_organic_posts(
    *,
    lookback_days: int = 30,
    limit: int = 25,
    min_impressions: int = MIN_IMPRESSIONS_DEFAULT,
) -> Dict[str, Any]:
    """
    Fetch organic metrics for published calendar FB posts and write DTL facts.
    No Ads API. Skips cleanly when FB not configured.
    """
    from agent.publishers.facebook import fetch_post_organic_metrics, is_facebook_configured

    as_of = _utc_now()
    if not is_facebook_configured():
        return {
            "source": "facebook_organic",
            "status": "skipped",
            "reason": "not_configured",
            "as_of": as_of,
        }

    entries = db_list_calendar_entries(status="published", platform="facebook", limit=limit)
    post_ids: List[str] = []
    for e in entries:
        pid = (e.get("fb_post_id") or "").strip()
        if pid and pid not in post_ids:
            post_ids.append(pid)

    metrics_rows: List[Dict[str, Any]] = []
    for pid in post_ids:
        m = fetch_post_organic_metrics(pid)
        if not m.get("ok"):
            continue
        engagements = float(m.get("engagements") or 0)
        impressions = m.get("impressions")
        # Proxy denominator when insights missing: max(engagements, 1) → ER unstable;
        # use engagements-as-score and treat impressions as engagements for relative lift.
        if impressions is None or int(impressions) <= 0:
            impressions_f = max(engagements, 1.0)
            er = engagements / impressions_f
            conf = 0.6
            quality_clean = False
        else:
            impressions_f = float(impressions)
            if impressions_f < float(min_impressions):
                logger.info(
                    "[dtl.fb_organic] skip low impressions post=%s imp=%s",
                    pid,
                    impressions_f,
                )
                continue
            er = engagements / impressions_f
            conf = 1.0 if m.get("insights_ok") else 0.8
            quality_clean = True
        link_clicks = m.get("link_clicks")
        metrics_rows.append(
            {
                "post_id": pid,
                "engagements": engagements,
                "impressions": impressions_f,
                "er": er,
                "link_clicks": float(link_clicks) if link_clicks is not None else None,
                "confidence": conf,
                "quality_clean": quality_clean,
            }
        )

    payload = {
        "lookback_days": lookback_days,
        "post_ids": post_ids,
        "metrics": metrics_rows,
        "min_impressions": min_impressions,
    }
    ingest_id = db_insert_marketing_raw_ingest(
        {
            "source": "facebook_organic",
            "fetched_at": as_of,
            "checksum": payload_checksum(payload),
            "payload": payload,
            "window_label": WINDOW,
            "status": "ok" if metrics_rows else "degraded",
        }
    )

    facts_written = 0
    if not metrics_rows:
        logger.info("[dtl.fb_organic] no metrics posts=%s", len(post_ids))
        return {
            "source": "facebook_organic",
            "status": "degraded" if post_ids else "ok",
            "ingest_id": ingest_id,
            "posts": len(post_ids),
            "facts_written": 0,
            "as_of": as_of,
        }

    avg_er = sum(r["er"] for r in metrics_rows) / len(metrics_rows)
    click_rows = [r for r in metrics_rows if r.get("link_clicks") is not None]
    avg_clicks = (
        sum(float(r["link_clicks"]) for r in click_rows) / len(click_rows)
        if click_rows
        else None
    )

    db_upsert_marketing_fact(
        {
            "metric_key": "organic_er_baseline_30d",
            "channel": "facebook",
            "window_label": WINDOW,
            "value": float(avg_er),
            "confidence": 1.0,
            "as_of": as_of,
            "source_ingest_id": ingest_id,
            "dims": {"n": len(metrics_rows)},
        }
    )
    facts_written += 1

    for row in metrics_rows:
        pid = row["post_id"]
        dims = {"post_id": pid, "quality_clean": row["quality_clean"]}
        for metric_key, value in (
            ("organic_impressions", row["impressions"]),
            ("organic_engagements", row["engagements"]),
            ("organic_er_pct", row["er"] * 100.0),
        ):
            db_upsert_marketing_fact(
                {
                    "metric_key": metric_key,
                    "channel": "facebook",
                    "window_label": WINDOW,
                    "value": float(value),
                    "confidence": float(row["confidence"]),
                    "as_of": as_of,
                    "source_ingest_id": ingest_id,
                    "dims": dims,
                }
            )
            facts_written += 1

        lift = _lift_pct(row["er"], avg_er)
        if lift is not None and row["quality_clean"]:
            db_upsert_marketing_fact(
                {
                    "metric_key": "organic_er_lift_pct",
                    "channel": "facebook",
                    "window_label": WINDOW,
                    "value": float(lift),
                    "confidence": float(row["confidence"]),
                    "as_of": as_of,
                    "source_ingest_id": ingest_id,
                    "dims": dims,
                }
            )
            facts_written += 1

        if row.get("link_clicks") is not None:
            db_upsert_marketing_fact(
                {
                    "metric_key": "organic_link_clicks",
                    "channel": "facebook",
                    "window_label": WINDOW,
                    "value": float(row["link_clicks"]),
                    "confidence": float(row["confidence"]),
                    "as_of": as_of,
                    "source_ingest_id": ingest_id,
                    "dims": dims,
                }
            )
            facts_written += 1
            if avg_clicks is not None and avg_clicks > 0 and row["quality_clean"]:
                clift = _lift_pct(float(row["link_clicks"]), avg_clicks)
                if clift is not None:
                    db_upsert_marketing_fact(
                        {
                            "metric_key": "organic_link_clicks_lift_pct",
                            "channel": "facebook",
                            "window_label": WINDOW,
                            "value": float(clift),
                            "confidence": float(row["confidence"]),
                            "as_of": as_of,
                            "source_ingest_id": ingest_id,
                            "dims": dims,
                        }
                    )
                    facts_written += 1

    logger.info(
        "[dtl.fb_organic] posts=%s metrics=%s facts=%s ingest_id=%s",
        len(post_ids),
        len(metrics_rows),
        facts_written,
        ingest_id,
    )
    return {
        "source": "facebook_organic",
        "status": "ok",
        "ingest_id": ingest_id,
        "posts": len(post_ids),
        "metrics": len(metrics_rows),
        "facts_written": facts_written,
        "as_of": as_of,
    }
