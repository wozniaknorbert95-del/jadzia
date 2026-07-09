"""Brand Strategist — brief + playbook → BrandStrategySpec (Brain2)."""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any

from agent.inspire.brand_strategy_spec import (
    BrandStrategySpec,
    ColorStrategy,
    PositioneringRules,
    TypographyRules,
)
from agent.inspire.tier_resolver import TierMeta

Positionering = str


def default_playbook_path() -> Path:
    env = os.getenv("DA_MARKETING_PLAYBOOK_PATH", "").strip()
    if env:
        return Path(env)
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root.parent / "zzpackage.flexgrafik.nl" / "brain-design-agent" / "marketing-playbook-nl-zzp.json"


def default_panel_map_path() -> Path:
    env = os.getenv("DA_PANEL_MAP_PATH", "").strip()
    if env:
        return Path(env)
    repo_root = Path(__file__).resolve().parents[2]
    return repo_root.parent / "zzpackage.flexgrafik.nl" / "brain-design-agent" / "panel-map.json"


def load_playbook(path: Path | None = None) -> dict[str, Any]:
    playbook_path = path or default_playbook_path()
    if not playbook_path.is_file():
        raise FileNotFoundError(f"marketing playbook not found: {playbook_path}")
    return json.loads(playbook_path.read_text(encoding="utf-8"))


def load_panel_map(path: Path | None = None) -> dict[str, Any]:
    panel_path = path or default_panel_map_path()
    if not panel_path.is_file():
        return {}
    return json.loads(panel_path.read_text(encoding="utf-8"))


def _match_branche_cluster(branche: str, playbook: dict[str, Any]) -> str:
    lowered = branche.lower()
    clusters = playbook.get("branche_clusters", {})
    for cluster_id, cfg in clusters.items():
        for kw in cfg.get("match_keywords", []):
            if kw.lower() in lowered:
                return cluster_id
    return "it_zzp"


def _normalize_positionering(raw: str, cluster_cfg: dict[str, Any]) -> str:
    val = (raw or "").lower().strip()
    if val in ("strak", "opvallend", "balanced"):
        return val
    default = cluster_cfg.get("positionering_default", "balanced")
    return default if default in ("strak", "opvallend", "balanced") else "balanced"


def _panels_for_sku(sku: str, panel_map: dict[str, Any], tier_key: str) -> list[str]:
    sku_panels = panel_map.get("sku_active_panels", {}).get(sku)
    if sku_panels:
        return list(sku_panels)
    defaults = panel_map.get("default_panels_by_tier", {})
    return list(defaults.get(tier_key, ["deur"]))


def produce_brand_strategy(
    *,
    branche: str,
    diensten: str,
    doelgroep: str,
    positionering: str,
    brand_colors: list[str],
    tier_b: TierMeta,
    tier_a: TierMeta,
    playbook: dict[str, Any] | None = None,
    panel_map: dict[str, Any] | None = None,
) -> BrandStrategySpec:
    """Rule-engine strategist from NL ZZP playbook (no LLM required for MVP)."""
    pb = playbook or load_playbook()
    pm = panel_map if panel_map is not None else load_panel_map()

    cluster_id = _match_branche_cluster(branche, pb)
    cluster_cfg = pb.get("branche_clusters", {}).get(cluster_id, {})
    pos = _normalize_positionering(positionering, cluster_cfg)
    pos_rules_raw = pb.get("positionering_rules", {}).get(pos, {})

    hierarchy = [h.get("element", "") for h in pb.get("message_hierarchy", []) if h.get("element")]
    if not hierarchy:
        hierarchy = ["logo", "bedrijfsnaam", "telefoon"]

    typo_defaults = pb.get("typography_defaults", {})
    typography = TypographyRules(
        naam_min_px=int(typo_defaults.get("naam_min_px", 36)),
        naam_weight=str(typo_defaults.get("naam_weight", "bold")),
        phone_min_px=int(typo_defaults.get("phone_min_px", 28)),
        slogan_max_px=int(typo_defaults.get("slogan_max_px", 24)),
        website_max_px=int(typo_defaults.get("website_max_px", 20)),
    )

    primary = brand_colors[0] if brand_colors else "#111111"
    diensten_emphasis = cluster_cfg.get("diensten_emphasis_nl", "Professionele service")
    tier_b_law = pb.get("tier_visual_law", {}).get("tier_b", {})
    tier_a_law = pb.get("tier_visual_law", {}).get("tier_a", {})

    return BrandStrategySpec(
        branche_cluster=cluster_id,
        positionering_rules=PositioneringRules(
            whitespace_pct=float(pos_rules_raw.get("whitespace_pct", 0.4)),
            coverage_target_b=float(pos_rules_raw.get("coverage_target_b", 0.35)),
            coverage_target_a=float(pos_rules_raw.get("coverage_target_a", 0.55)),
            layout_nl=str(pos_rules_raw.get("layout_nl", "")),
        ),
        message_hierarchy=hierarchy,
        active_panels_b=_panels_for_sku(tier_b.sku, pm, "tier_b"),
        active_panels_a=_panels_for_sku(tier_a.sku, pm, "tier_a"),
        typography=typography,
        color_strategy=ColorStrategy(primary=primary, accent_use="blocks"),
        sales_angle_nl=f"{diensten_emphasis} voor {doelgroep or 'lokale klanten'} — {cluster_cfg.get('visual_tone', 'professional')}",
        wizard_product_story_nl=(
            f"{tier_b_law.get('label_nl', 'Smart Start')} ({tier_b.sku}) vs "
            f"{tier_a_law.get('label_nl', 'Premium Presence')} ({tier_a.sku})"
        ),
        positionering=pos,  # type: ignore[arg-type]
    )
