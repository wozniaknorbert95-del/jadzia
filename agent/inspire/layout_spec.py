"""Pydantic models for LayoutSpec (Brain3 output)."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ElementAnchor(BaseModel):
    x_pct: float
    y_pct: float
    w_pct: float
    h_pct: float


class ElementStyle(BaseModel):
    size_px: int = 32
    color: str = "#111111"
    weight: str = "normal"


class LayoutElement(BaseModel):
    type: Literal["logo", "bedrijfsnaam", "telefoon", "website", "slogan", "accent_graphic"]
    anchor: ElementAnchor
    text_from_brief: bool = False
    style: ElementStyle = Field(default_factory=ElementStyle)


class LayoutPanel(BaseModel):
    id: Literal["deur", "zij", "achter", "kap"]
    elements: list[LayoutElement] = Field(default_factory=list)


class LayoutSpec(BaseModel):
    variant: Literal["tier_b", "tier_a"]
    sku: str
    panels: list[LayoutPanel] = Field(default_factory=list)
    fal_background_prompt: str
    fal_negative_prompt: str = ""
    compliance_checks: list[str] = Field(default_factory=list)
