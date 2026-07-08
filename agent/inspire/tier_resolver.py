"""Resolve Mockup B/A SKUs from brain-design-agent tier-matrix.json."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class TierMeta:
    sku: str
    coverage: str
    category: str
    wizard_group: str
    price_suggested: float


def default_matrix_path() -> Path:
    env = os.getenv("DA_TIER_MATRIX_PATH", "").strip()
    if env:
        return Path(env)
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root.parent / "zzpackage.flexgrafik.nl" / "brain-design-agent" / "tier-matrix.json"


def load_tier_matrix(path: Path | None = None) -> dict[str, Any]:
    matrix_path = path or default_matrix_path()
    if not matrix_path.is_file():
        raise FileNotFoundError(f"tier matrix not found: {matrix_path}")
    return json.loads(matrix_path.read_text(encoding="utf-8"))


def _entry_to_meta(entry: dict[str, Any]) -> TierMeta:
    return TierMeta(
        sku=str(entry["sku"]),
        coverage=str(entry.get("coverage", "")),
        category=str(entry.get("category", "")),
        wizard_group=str(entry.get("wizard_group", "")),
        price_suggested=float(entry.get("price_suggested", 0)),
    )


def _find_entry(entries: list[dict[str, Any]], sku: str) -> dict[str, Any] | None:
    for entry in entries:
        if entry.get("sku") == sku:
            return entry
    return None


def _default_entry(entries: list[dict[str, Any]], flag: str) -> dict[str, Any] | None:
    for entry in entries:
        if entry.get(flag):
            return entry
    return entries[0] if entries else None


def _entry_by_category(entries: list[dict[str, Any]], category: str) -> dict[str, Any] | None:
    for entry in entries:
        if entry.get("category") == category:
            return entry
    return None


def resolve_tier_skus(
    vehicle: str,
    brief: dict[str, Any],
    *,
    matrix_path: Path | None = None,
) -> tuple[TierMeta, TierMeta]:
    """Return (tier_b, tier_a) metadata for inspire prompts and reco."""
    matrix = load_tier_matrix(matrix_path)
    vehicle_cfg = matrix.get("vehicles", {}).get(vehicle)
    if not vehicle_cfg:
        raise ValueError(f"unknown vehicle: {vehicle}")

    b_entries: list[dict[str, Any]] = list(vehicle_cfg.get("mockup_b", []))
    a_entries: list[dict[str, Any]] = list(vehicle_cfg.get("mockup_a", []))
    if not b_entries or not a_entries:
        raise ValueError(f"tier matrix incomplete for vehicle: {vehicle}")

    override_b = brief.get("mockup_b_sku")
    override_a = brief.get("mockup_a_sku")
    if override_b and override_a:
        b_entry = _find_entry(b_entries, str(override_b))
        a_entry = _find_entry(a_entries, str(override_a))
        if not b_entry or not a_entry:
            raise ValueError("mockup_b_sku or mockup_a_sku not in tier matrix")
        return _entry_to_meta(b_entry), _entry_to_meta(a_entry)

    b_entry: dict[str, Any] | None = None
    a_entry: dict[str, Any] | None = None

    vehicle_use = str(brief.get("vehicle_use", "")).lower()
    branding_goal = str(brief.get("branding_goal", "")).lower()
    positionering = str(brief.get("positionering") or brief.get("stijl", "balanced")).lower()

    if vehicle == "caddy" and vehicle_use == "private":
        b_entry = _find_entry(b_entries, "MA-005")

    if branding_goal in ("permanent", "permanent_low_budget"):
        b_entry = _entry_by_category(b_entries, "set")
        if vehicle == "caddy" and b_entry is None:
            b_entry = _find_entry(b_entries, "CS-SET-LOGO-CONTACT")

    if branding_goal == "max_visibility" or positionering == "opvallend":
        wrap = _entry_by_category(a_entries, "wrap")
        if wrap:
            a_entry = wrap

    if b_entry is None:
        b_entry = _default_entry(b_entries, "is_default_b") or b_entries[0]
    if a_entry is None:
        a_entry = _default_entry(a_entries, "is_default_a") or a_entries[0]

    return _entry_to_meta(b_entry), _entry_to_meta(a_entry)
