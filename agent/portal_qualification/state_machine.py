"""Deterministic qualification state machine (server-owned steps)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

from agent.portal_qualification.preset_recommender import PresetRecommender
from agent.portal_qualification.slot_extractor import extract_slot_value
from agent.portal_qualification.taxonomy import get_step_config, ui_suggestions_for_slot

STEP_ORDER = ("greeting", "q1_industry", "q2_goal", "q3_vehicle", "q4_budget", "recommend", "done")


class PortalQualificationStateMachine:
    def __init__(self) -> None:
        self._recommender = PresetRecommender()

    def process_turn(
        self,
        *,
        step: str,
        message: str,
        profile: Dict[str, Optional[str]],
        consent_lead_storage: bool = False,
    ) -> Dict[str, Any]:
        step = step or "greeting"
        if step not in STEP_ORDER:
            step = "greeting"

        if step == "greeting":
            return self._advance_from_greeting(message, profile)

        if step == "recommend":
            return self._recommendation_response(profile, consent_lead_storage)

        if step == "done":
            return {
                "reply": (
                    "Je advies staat hierboven. Gebruik de knop om verder te gaan, "
                    "of stel gerust nog een korte vraag via ons contactformulier."
                ),
                "step_next": "done",
                "ui_suggestions": [],
                "qualification_profile": dict(profile),
                "recommended_preset_id": None,
                "wizard_deep_link": None,
                "cta": None,
                "lead_saved": False,
            }

        return self._capture_slot(step, message, profile, consent_lead_storage)

    def _advance_from_greeting(
        self, message: str, profile: Dict[str, Optional[str]]
    ) -> Dict[str, Any]:
        industry = extract_slot_value("industry", message)
        if industry:
            profile = dict(profile)
            profile["industry"] = industry
            next_step = "q2_goal"
            next_cfg = get_step_config(next_step)
            return {
                "reply": next_cfg["question_nl"],
                "step_next": next_step,
                "ui_suggestions": ui_suggestions_for_slot("goal"),
                "qualification_profile": profile,
                "recommended_preset_id": None,
                "wizard_deep_link": None,
                "cta": None,
                "lead_saved": False,
            }

        cfg = get_step_config("greeting")
        return {
            "reply": cfg["question_nl"],
            "step_next": "q1_industry",
            "ui_suggestions": ui_suggestions_for_slot("industry"),
            "qualification_profile": dict(profile),
            "recommended_preset_id": None,
            "wizard_deep_link": None,
            "cta": None,
            "lead_saved": False,
        }

    def _capture_slot(
        self,
        step: str,
        message: str,
        profile: Dict[str, Optional[str]],
        consent_lead_storage: bool,
    ) -> Dict[str, Any]:
        cfg = get_step_config(step)
        slot = cfg.get("slot")
        if not slot:
            return self._advance_from_greeting(message, profile)

        value = extract_slot_value(slot, message)
        if not value:
            return {
                "reply": f"Kun je een van de opties kiezen? {cfg['question_nl']}",
                "step_next": step,
                "ui_suggestions": ui_suggestions_for_slot(slot),
                "qualification_profile": dict(profile),
                "recommended_preset_id": None,
                "wizard_deep_link": None,
                "cta": None,
                "lead_saved": False,
            }

        profile = dict(profile)
        profile[slot] = value

        next_step = cfg["step_next"]
        if next_step == "recommend":
            return self._recommendation_response(profile, consent_lead_storage)

        next_cfg = get_step_config(next_step)
        next_slot = next_cfg.get("slot")
        suggestions: List[Dict[str, str]] = (
            ui_suggestions_for_slot(next_slot) if next_slot else []
        )
        return {
            "reply": next_cfg["question_nl"],
            "step_next": next_step,
            "ui_suggestions": suggestions,
            "qualification_profile": profile,
            "recommended_preset_id": None,
            "wizard_deep_link": None,
            "cta": None,
            "lead_saved": False,
        }

    def _recommendation_response(
        self, profile: Dict[str, Optional[str]], consent_lead_storage: bool
    ) -> Dict[str, Any]:
        preset_id = self._recommender.recommend(profile)
        cta = self._recommender.build_cta(preset_id)
        wizard_link = (
            self._recommender.build_wizard_deep_link(preset_id)
            if cta["type"] == "wizard"
            else None
        )
        lead_saved = False

        return {
            "reply": self._recommender.recommendation_reply_nl(preset_id),
            "step_next": "done",
            "ui_suggestions": [],
            "qualification_profile": dict(profile),
            "recommended_preset_id": preset_id,
            "wizard_deep_link": wizard_link,
            "cta": cta,
            "lead_saved": lead_saved,
        }
