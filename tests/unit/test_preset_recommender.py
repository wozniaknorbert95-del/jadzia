"""Unit tests for deterministic preset recommendation."""

import pytest

from agent.portal_qualification.preset_recommender import PresetRecommender


@pytest.fixture
def recommender():
    return PresetRecommender()


class TestPresetRecommender:
    @pytest.mark.parametrize(
        "profile,expected",
        [
            ({"vehicle": "vloot", "goal": "meer_klanten"}, "professional-flota"),
            ({"goal": "vloot_groei", "vehicle": "bus"}, "professional-flota"),
            ({"budget_tier": "700_plus", "vehicle": "bus"}, "professional-flota"),
            ({"budget_tier": "onder_300", "vehicle": "auto"}, "starter-zzp"),
            (
                {"vehicle": "geen", "goal": "professioneler_imago", "budget_tier": "300_700"},
                "starter-zzp",
            ),
            (
                {"goal": "voertuig_reclame", "vehicle": "bus", "budget_tier": "300_700"},
                "groeier",
            ),
            ({"vehicle": "auto", "goal": "meer_klanten", "budget_tier": "onbekend"}, "groeier"),
            ({"vehicle": "bus", "goal": "meer_klanten", "budget_tier": "300_700"}, "groeier"),
            ({"industry": "bouw", "goal": "meer_klanten", "vehicle": "geen"}, "groeier"),
            ({"budget_tier": "300_700", "vehicle": "geen", "goal": "meer_klanten"}, "groeier"),
        ],
    )
    def test_recommend_preset(self, recommender, profile, expected):
        assert recommender.recommend(profile) == expected

    def test_build_wizard_deep_link_contains_preset_and_utm(self, recommender):
        url = recommender.build_wizard_deep_link("groeier")
        assert "preset=groeier" in url
        assert "utm_source=portal_qual" in url
        assert url.startswith("https://zzpackage.flexgrafik.nl/wizard/")

    def test_build_cta_wizard_for_groeier(self, recommender):
        cta = recommender.build_cta("groeier")
        assert cta["type"] == "wizard"
        assert "wizard" in cta["url"]

    def test_build_cta_whatsapp_for_flota(self, recommender):
        cta = recommender.build_cta("professional-flota")
        assert cta["type"] == "whatsapp"
        assert cta["url"].startswith("https://wa.me/")
