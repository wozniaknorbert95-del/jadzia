"""Optional Haiku slot extraction when synonym match fails."""

from __future__ import annotations

import json
import logging
import os
from typing import Optional

from anthropic import AsyncAnthropic

from agent.portal_qualification.taxonomy import get_enum_values, load_taxonomy

logger = logging.getLogger(__name__)

_client: Optional[AsyncAnthropic] = None


def _get_client() -> Optional[AsyncAnthropic]:
    global _client
    key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if not key:
        return None
    if _client is None:
        _client = AsyncAnthropic(api_key=key)
    return _client


async def extract_slot_llm(slot: str, message: str) -> Optional[str]:
    """Map free-text NL to taxonomy enum via structured Haiku output."""
    if not message or not message.strip():
        return None

    enabled = os.getenv("PORTAL_QUAL_LLM_SLOTS", "1").strip().lower()
    if enabled in ("0", "false", "no", "off"):
        return None

    client = _get_client()
    if not client:
        return None

    taxonomy = load_taxonomy()
    enum_block = taxonomy["enums"].get(slot)
    if not enum_block:
        return None

    allowed = get_enum_values(slot)
    labels = enum_block.get("labels_nl", {})

    system = (
        "Je bent een NL slot-extractor. Map gebruikersinput naar exact één enum-waarde. "
        "Antwoord ALLEEN met JSON: {\"value\": \"<enum>\"} of {\"value\": null} "
        f"Toegestane waarden: {allowed}. Labels: {labels}."
    )

    try:
        from agent.agent import MODEL_HAIKU

        response = await client.messages.create(
            model=MODEL_HAIKU,
            max_tokens=64,
            system=system,
            messages=[{"role": "user", "content": message[:500]}],
        )
        raw = response.content[0].text.strip()
        if "{" in raw:
            raw = raw[raw.find("{") : raw.rfind("}") + 1]
        parsed = json.loads(raw)
        value = parsed.get("value")
        if value in allowed:
            return value
    except Exception as e:
        logger.warning("[PortalQual] LLM slot extract failed for %s: %s", slot, e)

    return None
