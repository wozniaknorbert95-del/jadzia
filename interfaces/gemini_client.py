"""
Jadzia: thin Gemini client for research endpoints.
Optional dependency; safe to import when GOOGLE_API_KEY is set and SDK installed.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional


class NotConfigured(RuntimeError):
    pass


@dataclass
class ResearchReply:
    text: str
    model: str = "gemini-3.1-pro"


class GeminiClient:
    def __init__(self, model: str = "gemini-3.1-pro") -> None:
        self.model = model

    def _sdk(self):
        try:
            import google.generativeai as genai  # type: ignore
        except Exception as e:
            raise NotConfigured("google-generativeai SDK not installed") from e
        return genai

    def generate(self, prompt: str, *, temperature: float = 0.2) -> ResearchReply:
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise NotConfigured("GOOGLE_API_KEY is not set")
        genai = self._sdk()
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel(self.model)
        resp = model.generate_content(prompt, generation_config={"temperature": temperature})
        text = getattr(resp, "text", "") or ""
        return ResearchReply(text=text, model=self.model)
