"""Load portal qualification taxonomy (SSoT mirror from flexgrafik-meta)."""

from __future__ import annotations

import json
from functools import lru_cache
from pathlib import Path
from typing import Any, Dict, List, Optional

_DATA_DIR = Path(__file__).resolve().parent / "data"


@lru_cache(maxsize=1)
def load_taxonomy() -> Dict[str, Any]:
    path = _DATA_DIR / "taxonomy.json"
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def get_step_config(step: str) -> Dict[str, Any]:
    taxonomy = load_taxonomy()
    steps = taxonomy.get("steps", {})
    if step not in steps:
        raise KeyError(f"Unknown qualification step: {step}")
    return steps[step]


def get_enum_values(slot: str) -> List[str]:
    taxonomy = load_taxonomy()
    enum_block = taxonomy["enums"][slot]
    return list(enum_block["values"])


def ui_suggestions_for_slot(slot: str) -> List[Dict[str, str]]:
    taxonomy = load_taxonomy()
    enum_block = taxonomy["enums"][slot]
    labels = enum_block.get("labels_nl", {})
    return [{"value": value, "label_nl": labels.get(value, value)} for value in enum_block["values"]]


def label_for_value(slot: str, value: str) -> str:
    taxonomy = load_taxonomy()
    return taxonomy["enums"][slot]["labels_nl"].get(value, value)


def utm_defaults() -> Dict[str, str]:
    return dict(load_taxonomy().get("utm_defaults", {}))
