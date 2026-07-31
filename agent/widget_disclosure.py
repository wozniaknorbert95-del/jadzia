"""COM-AI-50 canonical AI disclosure for public widget chat (NL)."""

from __future__ import annotations

# Locked by Founder ACCEPT COM-AI-50 (2026-07-31). Do not edit without new HITL.
AI_DISCLOSURE_NL = (
    "Je chat met een AI-assistent van FlexGrafik. "
    "Wil je een mens? Laat het weten — we nemen over."
)


def apply_widget_ai_disclosure(reply: str, *, is_first_turn: bool) -> tuple[str, str]:
    """
    Always return the canonical disclosure string.

    On the first turn of a session, prefix the customer-visible reply when missing
    so clients that only render `reply` still surface Art.50 disclosure.
    """
    text = (reply or "").strip()
    if is_first_turn and AI_DISCLOSURE_NL not in text:
        text = f"{AI_DISCLOSURE_NL}\n\n{text}".strip() if text else AI_DISCLOSURE_NL
    return text, AI_DISCLOSURE_NL
