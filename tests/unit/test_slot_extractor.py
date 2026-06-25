"""Unit tests for NL slot extraction."""

import pytest

from agent.portal_qualification.slot_extractor import extract_slot_value


@pytest.mark.parametrize(
    "slot,message,expected",
    [
        ("industry", "Bouw", "bouw"),
        ("industry", "ik werk in de bouw", "bouw"),
        ("goal", "meer klanten", "meer_klanten"),
        ("goal", "voertuig reclame", "voertuig_reclame"),
        ("vehicle", "bedrijfsbus", "bus"),
        ("vehicle", "geneeskunde", None),
        ("vehicle", "nee", "geen"),
        ("budget_tier", "300-700", "300_700"),
        ("budget_tier", "€300 – €700", "300_700"),
        ("budget_tier", "onder 300", "onder_300"),
    ],
)
def test_extract_slot_value(slot, message, expected):
    assert extract_slot_value(slot, message) == expected
