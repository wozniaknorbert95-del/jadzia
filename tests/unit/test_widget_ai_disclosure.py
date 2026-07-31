"""COM-AI-50-SHIP — canonical widget AI disclosure contracts."""

from agent.widget_disclosure import AI_DISCLOSURE_NL, apply_widget_ai_disclosure
from core.models import CustomerChatResponse


def test_canonical_disclosure_matches_founder_accept():
    assert "AI-assistent van FlexGrafik" in AI_DISCLOSURE_NL
    assert "Wil je een mens?" in AI_DISCLOSURE_NL
    assert AI_DISCLOSURE_NL == (
        "Je chat met een AI-assistent van FlexGrafik. "
        "Wil je een mens? Laat het weten — we nemen over."
    )


def test_first_turn_prefixes_reply():
    reply, disclosure = apply_widget_ai_disclosure("Hallo!", is_first_turn=True)
    assert disclosure == AI_DISCLOSURE_NL
    assert reply.startswith(AI_DISCLOSURE_NL)
    assert "Hallo!" in reply


def test_later_turn_keeps_reply_but_still_returns_disclosure():
    reply, disclosure = apply_widget_ai_disclosure("Nog een vraag", is_first_turn=False)
    assert disclosure == AI_DISCLOSURE_NL
    assert reply == "Nog een vraag"
    assert not reply.startswith(AI_DISCLOSURE_NL)


def test_first_turn_idempotent_if_already_present():
    seeded = f"{AI_DISCLOSURE_NL}\n\nHallo!"
    reply, _ = apply_widget_ai_disclosure(seeded, is_first_turn=True)
    assert reply.count(AI_DISCLOSURE_NL) == 1


def test_response_model_accepts_ai_disclosure():
    r = CustomerChatResponse(reply="x", ai_disclosure=AI_DISCLOSURE_NL)
    assert r.ai_disclosure == AI_DISCLOSURE_NL
