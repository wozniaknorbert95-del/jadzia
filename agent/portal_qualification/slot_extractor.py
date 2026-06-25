"""Normalize free-text NL input to taxonomy enum values (no LLM)."""

from __future__ import annotations

import re
from typing import Optional

from agent.portal_qualification.taxonomy import get_enum_values, load_taxonomy


def extract_slot_value(slot: str, message: str) -> Optional[str]:
    """Map user message to enum value via exact key or synonym match."""
    if not message or not message.strip():
        return None

    normalized = _normalize(message)
    taxonomy = load_taxonomy()
    enum_block = taxonomy["enums"][slot]

    for value in enum_block["values"]:
        if normalized == _normalize(value):
            return value
        label = enum_block["labels_nl"].get(value, "")
        if label and normalized == _normalize(label):
            return value

    for value, synonyms in enum_block.get("synonyms_nl", {}).items():
        for synonym in synonyms:
            if _matches_synonym(normalized, synonym):
                return value

    enum_key = normalized.replace(" ", "_")
    if enum_key in get_enum_values(slot):
        return enum_key

    return None


def _normalize(text: str) -> str:
    text = text.lower().strip()
    text = text.replace("€", "").replace("–", "-").replace("—", "-")
    return " ".join(text.split())


def _matches_synonym(normalized: str, synonym: str) -> bool:
    """Avoid short-substring false positives (e.g. geen in geneeskunde)."""
    syn = _normalize(synonym)
    if not syn:
        return False
    if normalized == syn:
        return True

    words = normalized.split()
    if syn in words:
        return True

    if " " in syn and syn in normalized:
        return True

    if len(syn) >= 5 and syn in normalized:
        return True

    if re.search(rf"\b{re.escape(syn)}\b", normalized):
        return True

    return False
