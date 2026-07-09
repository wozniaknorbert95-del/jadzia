"""Pydantic models for BrandStrategySpec (Brain2 output)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class PositioneringRules(BaseModel):
    whitespace_pct: float = 0.4
    coverage_target_b: float = 0.35
    coverage_target_a: float = 0.55
    layout_nl: str = ""


class TypographyRules(BaseModel):
    naam_min_px: int = 36
    naam_weight: str = "bold"
    phone_min_px: int = 28
    slogan_max_px: int = 24
    website_max_px: int = 20


class ColorStrategy(BaseModel):
    primary: str = "#111111"
    accent_use: str = "blocks"


class BrandStrategySpec(BaseModel):
    branche_cluster: str
    positionering_rules: PositioneringRules
    message_hierarchy: list[str] = Field(default_factory=lambda: ["logo", "bedrijfsnaam", "telefoon"])
    active_panels_b: list[str] = Field(default_factory=lambda: ["deur"])
    active_panels_a: list[str] = Field(default_factory=lambda: ["deur", "zij", "achter"])
    typography: TypographyRules = Field(default_factory=TypographyRules)
    color_strategy: ColorStrategy = Field(default_factory=ColorStrategy)
    sales_angle_nl: str
    wizard_product_story_nl: str
    positionering: Literal["strak", "opvallend", "balanced"] = "balanced"
