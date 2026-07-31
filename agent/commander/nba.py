"""Deterministic Next Best Action (NBA) ranking for Mission Control Director Brief.

Score (research SoT, no ML):
  priority = money_proxy × p_close × urgency + risk_cost − uncertainty_penalty
"""

from __future__ import annotations

from typing import Any, Dict, List, Optional, Tuple

# Proxy weights — not displayed as €; honest ranking fuel only.
_MONEY_PROXY: Dict[str, float] = {
    "hot_lead": 100.0,
    "sales_cta": 85.0,
    "agent_error": 75.0,
    "publish_failed": 70.0,
    "wp_ticket": 55.0,
    "cs_followup": 50.0,
    "scheduled_publish_due": 45.0,
    "fb_post_pending": 40.0,
}

_P_CLOSE: Dict[str, float] = {
    "hot_lead": 0.75,
    "sales_cta": 0.70,
    "agent_error": 0.55,
    "publish_failed": 0.50,
    "wp_ticket": 0.50,
    "cs_followup": 0.55,
    "scheduled_publish_due": 0.45,
    "fb_post_pending": 0.40,
}

_OWNER: Dict[str, str] = {
    "hot_lead": "Sales / Dowódca",
    "sales_cta": "Sales / Dowódca",
    "cs_followup": "Customer Success",
    "fb_post_pending": "Marketing",
    "scheduled_publish_due": "Marketing",
    "publish_failed": "Marketing",
    "wp_ticket": "Ops / WP",
    "agent_error": "Ops / Agents",
}

_COST: Dict[str, str] = {
    "hot_lead": "Lead cools — lost Wizard conversion window",
    "sales_cta": "Brief CTA ages — follow-up SLA miss",
    "fb_post_pending": "Publish slip — organic slot wasted",
    "scheduled_publish_due": "Schedule miss — calendar trust drop",
    "publish_failed": "Failed publish stays broken — audience gap",
    "agent_error": "Agent silent — ops backlog grows",
    "wp_ticket": "WP defect lingers — site/ops risk",
    "cs_followup": "Post-sale follow-up slips — retention risk",
}

_SEVERITY_RANK = {"CRITICAL": 0, "ACTION": 1, "INFO": 2}


def _sla_urgency(sla_status: str, age_hours: float) -> float:
    base = {"RED": 1.6, "AMBER": 1.25, "OK": 1.0}.get(
        (sla_status or "OK").upper(), 1.0
    )
    age_boost = min(1.0 + max(age_hours, 0.0) / 48.0, 1.5)
    return base * age_boost


def score_queue_item(item: Dict[str, Any]) -> Dict[str, float]:
    """Return score parts + total for a CRITICAL/ACTION queue item."""
    qtype = str(item.get("queue_type") or "")
    money = float(_MONEY_PROXY.get(qtype, 30.0))
    p_close = float(_P_CLOSE.get(qtype, 0.45))
    urgency = _sla_urgency(
        str(item.get("sla_status") or "OK"),
        float(item.get("age_hours") or 0.0),
    )
    risk = 40.0 if (item.get("severity") or "").upper() == "CRITICAL" else 15.0
    confidence = float(item.get("confidence") if item.get("confidence") is not None else 0.85)
    confidence = max(0.0, min(confidence, 1.0))
    uncertainty = (1.0 - confidence) * 25.0
    total = money * p_close * urgency + risk - uncertainty
    return {
        "money_proxy": round(money, 2),
        "p_close": round(p_close, 3),
        "urgency": round(urgency, 3),
        "risk_cost": round(risk, 2),
        "uncertainty_penalty": round(uncertainty, 2),
        "score": round(total, 3),
    }


def _cta_for(item: Dict[str, Any]) -> Dict[str, str]:
    qtype = item.get("queue_type")
    payload = item.get("payload") or {}
    if qtype in ("hot_lead", "sales_cta") and (payload.get("lead_id") or payload.get("id")):
        return {
            "label": "Potwierdź lead",
            "action": "lead_ack",
            "target": str(payload.get("lead_id") or payload.get("id")),
        }
    if qtype == "cs_followup" and payload.get("ticket_id"):
        return {
            "label": "Potwierdź ticket",
            "action": "ticket_ack",
            "target": str(payload["ticket_id"]),
        }
    if qtype in ("fb_post_pending", "scheduled_publish_due", "publish_failed"):
        return {"label": "Focus queue", "action": "focus_queue", "target": "queue"}
    return {"label": "Focus queue", "action": "focus_queue", "target": "queue"}


def _approval_class(item: Dict[str, Any]) -> str:
    qtype = item.get("queue_type")
    if qtype in ("hot_lead", "sales_cta", "cs_followup"):
        return "L1"
    return "L2"


def enrich_nba(item: Dict[str, Any]) -> Dict[str, Any]:
    """Attach NBA fields for Director primary card (mutates a copy)."""
    parts = score_queue_item(item)
    qtype = str(item.get("queue_type") or "")
    out = dict(item)
    out["nba_primary"] = True
    out["nba_score"] = parts["score"]
    out["nba_score_parts"] = parts
    out["why_now"] = item.get("escalation_reason") or f"Pending {qtype}"
    out["evidence_ts"] = item.get("created_at") or ""
    out["owner"] = _OWNER.get(qtype, "Dowódca")
    out["cta"] = _cta_for(item)
    out["cost_of_inaction"] = _COST.get(qtype, "Delay compounds ops / revenue risk")
    out["approval_class"] = _approval_class(item)
    return out


def rank_candidates(items: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Rank CRITICAL/ACTION only; INFO/stubs excluded by caller eligibility."""
    scored: List[Tuple[float, int, float, str, Dict[str, Any]]] = []
    for item in items:
        sev = (item.get("severity") or "").upper()
        if sev not in ("CRITICAL", "ACTION"):
            continue
        if item.get("queue_type") in ("ceo_stub", "analytics_stale", "weekly_brief_ready"):
            continue
        if item.get("source") == "brain_bus_ceo":
            continue
        parts = score_queue_item(item)
        scored.append(
            (
                -parts["score"],
                _SEVERITY_RANK.get(sev, 9),
                -float(item.get("age_hours") or 0.0),
                str(item.get("id") or ""),
                item,
            )
        )
    scored.sort(key=lambda t: (t[0], t[1], t[2], t[3]))
    return [t[4] for t in scored]


def build_director_brief(
    candidates: List[Dict[str, Any]],
    *,
    max_secondary: int = 2,
) -> Dict[str, Any]:
    """Select exactly one NBA primary + secondary list."""
    ranked = rank_candidates(candidates)
    if not ranked:
        return {"nba": None, "secondary": [], "ranked": []}
    nba = enrich_nba(ranked[0])
    secondary = ranked[1 : 1 + max(0, max_secondary)]
    return {"nba": nba, "secondary": secondary, "ranked": ranked}


def select_nba(candidates: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    brief = build_director_brief(candidates, max_secondary=0)
    return brief["nba"]
