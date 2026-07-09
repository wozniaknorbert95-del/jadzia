"""Unit tests for overlay renderer v2 vinyl typography."""

from __future__ import annotations

from agent.inspire.overlay_renderer import (
    SLOGAN_MAX_WORDS,
    _normalize_phone,
    _truncate_slogan,
)


def test_normalize_phone_dutch_mobile() -> None:
    assert _normalize_phone("0612345678") == "06-1234 5678"
    assert _normalize_phone("06-12345678") == "06-1234 5678"


def test_truncate_slogan_max_six_words() -> None:
    long = "one two three four five six seven eight"
    assert len(_truncate_slogan(long).split()) == SLOGAN_MAX_WORDS


def test_truncate_slogan_short_unchanged() -> None:
    short = "Conversion Systems Architect"
    assert _truncate_slogan(short) == short
