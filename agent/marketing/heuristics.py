"""Marketing Brain hard rules — heuristics first, LLM never overrides."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)

# Playbook floors
MARGIN_FLOOR_PCT = 0.40  # net_margin_pct floor (Profit Watchdog)
ATTRIBUTION_COVERAGE_FLOOR = 50.0
ORGANIC_WINNER_LIFT_PCT = 50.0


@dataclass
class Decision:
    proposed_action: str  # hold|alert_critical|propose_boost|block_scale
    heuristic_rule_id: str
    would_execute: bool
    governance_result: str  # allow|deny|review
    rationale_nl: str
    severity: str = "INFO"  # INFO|ACTION|CRITICAL
    dims: Dict[str, Any] = field(default_factory=dict)


def evaluate(facts_bundle: Dict[str, Any]) -> List[Decision]:
    """
    Evaluate DTL facts → ordered decisions (hard rules only).
    facts_bundle keys: quality_flags, margin_avg_pct, attribution_coverage_pct,
    organic_candidates (optional list), freshness_overall
    """
    decisions: List[Decision] = []

    flags = facts_bundle.get("quality_flags") or []
    red_flags = [
        f for f in flags
        if f.get("severity") in ("critical", "red") and f.get("active", 1)
    ]
    if red_flags:
        decisions.append(
            Decision(
                proposed_action="hold",
                heuristic_rule_id="HEU_DATA_QUALITY_RED",
                would_execute=False,
                governance_result="deny",
                rationale_nl=(
                    f"DTL ma {len(red_flags)} flag RED/critical — HOLD optymalizacji."
                ),
                severity="CRITICAL",
                dims={"flag_sources": [f.get("source") for f in red_flags]},
            )
        )

    margin_pct = facts_bundle.get("margin_avg_pct")
    if margin_pct is not None and margin_pct < MARGIN_FLOOR_PCT:
        decisions.append(
            Decision(
                proposed_action="block_scale",
                heuristic_rule_id="HEU_PROFIT_WATCHDOG",
                would_execute=True,
                governance_result="deny",
                rationale_nl=(
                    f"Net margin {margin_pct:.1%} < floor {MARGIN_FLOOR_PCT:.0%} — "
                    "BLOCK scale (Profit Watchdog)."
                ),
                severity="CRITICAL",
                dims={"margin_avg_pct": margin_pct, "floor": MARGIN_FLOOR_PCT},
            )
        )

    coverage = facts_bundle.get("attribution_coverage_pct")
    if coverage is not None and coverage < ATTRIBUTION_COVERAGE_FLOOR:
        decisions.append(
            Decision(
                proposed_action="hold",
                heuristic_rule_id="HEU_ATTRIBUTION_LOW",
                would_execute=False,
                governance_result="review",
                rationale_nl=(
                    f"Attribution coverage {coverage:.1f}% < {ATTRIBUTION_COVERAGE_FLOOR}% — "
                    "HOLD channel CPA calls."
                ),
                severity="ACTION",
                dims={"coverage_pct": coverage},
            )
        )

    for cand in facts_bundle.get("organic_candidates") or []:
        lift = float(cand.get("lift_pct") or 0)
        if lift >= ORGANIC_WINNER_LIFT_PCT and cand.get("quality_clean", True):
            decisions.append(
                Decision(
                    proposed_action="propose_boost",
                    heuristic_rule_id="HEU_ORGANIC_WINNER",
                    would_execute=True,
                    governance_result="review",
                    rationale_nl=(
                        f"Organic winner {cand.get('post_id', '?')}: "
                        f"ER/clicks +{lift:.0f}% vs 30d — rozważ boost Ads "
                        f"(paste-ready; MB nie tworzy kampanii)."
                    ),
                    severity="CRITICAL",
                    dims=cand,
                )
            )

    if not decisions:
        decisions.append(
            Decision(
                proposed_action="hold",
                heuristic_rule_id="HEU_NO_SIGNAL",
                would_execute=False,
                governance_result="allow",
                rationale_nl="Brak sygnału decyzyjnego — HOLD (observability).",
                severity="INFO",
            )
        )

    logger.info("[mb.heuristics] decisions=%s", len(decisions))
    return decisions
