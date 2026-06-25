"""Deterministic preset recommendation — mirrors preset-manifest business rules."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, Optional
from urllib.parse import quote as url_quote, urlencode

from agent.portal_qualification.taxonomy import utm_defaults

_DATA_DIR = Path(__file__).resolve().parent / "data"


@lru_cache(maxsize=1)
def _load_preset_rules() -> Dict[str, Any]:
    with (_DATA_DIR / "preset_rules.json").open(encoding="utf-8") as f:
        return json.load(f)


class PresetRecommender:
    """Pure rules engine — LLM must not select presets directly."""

    VALID_PRESETS = ("starter-zzp", "groeier", "professional-flota")

    def recommend(self, profile: Dict[str, Optional[str]]) -> str:
        industry = profile.get("industry")
        goal = profile.get("goal")
        vehicle = profile.get("vehicle")
        budget = profile.get("budget_tier")

        if vehicle == "vloot" or goal == "vloot_groei":
            return "professional-flota"

        if budget == "700_plus" and vehicle == "bus":
            return "professional-flota"

        if budget == "onder_300":
            return "starter-zzp"

        if vehicle == "geen" and goal == "professioneler_imago":
            return "starter-zzp"

        if goal == "voertuig_reclame" and vehicle in ("auto", "bus"):
            return "groeier"

        if vehicle in ("auto", "bus"):
            return "groeier"

        if budget == "300_700":
            return "groeier"

        if goal == "meer_klanten" and vehicle == "bus":
            return "groeier"

        # Industry does not change preset today; reserved for future copy personalization.
        _ = industry

        return "groeier"

    def preset_meta(self, preset_id: str) -> Dict[str, Any]:
        rules = _load_preset_rules()
        presets = rules["presets"]
        if preset_id not in presets:
            raise KeyError(f"Unknown preset: {preset_id}")
        return presets[preset_id]

    def build_wizard_deep_link(self, preset_id: str) -> str:
        rules = _load_preset_rules()
        base = rules["wizard_base_url"].rstrip("/") + "/"
        params = {"preset": preset_id, **utm_defaults()}
        return f"{base}?{urlencode(params)}"

    def build_cta(self, preset_id: str) -> Dict[str, str]:
        meta = self.preset_meta(preset_id)
        if meta.get("quote_mode"):
            quote_cta = meta.get("quote_cta", {})
            phone = quote_cta.get("whatsapp", "+31687286151")
            msg = quote_cta.get("message_nl", "Hoi FlexGrafik, ik wil een offerte.")
            return {
                "type": "whatsapp",
                "label_nl": "Vraag offerte via WhatsApp",
                "url": f"https://wa.me/{phone.lstrip('+')}?text={url_quote(msg)}",
            }
        return {
            "type": "wizard",
            "label_nl": "Start de Wizard →",
            "url": self.build_wizard_deep_link(preset_id),
        }

    def recommendation_reply_nl(self, preset_id: str) -> str:
        meta = self.preset_meta(preset_id)
        label = meta.get("label_nl", preset_id)
        tagline = meta.get("tagline_nl", "")
        if meta.get("quote_mode"):
            return (
                f"Op basis van je antwoorden past {label} het beste bij je: {tagline}. "
                "Dit traject loopt via een persoonlijke offerte — geen online checkout."
            )
        return (
            f"Op basis van je antwoorden raden we {label} aan: {tagline}. "
            "Je kunt direct starten in de Wizard met een voorgeselecteerd pakket."
        )
