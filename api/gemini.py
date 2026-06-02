"""Gemini service — thin integration wrapper for research queries."""

from __future__ import annotations

import os
from dataclasses import dataclass
from typing import Optional

from core.services import GeminiService


@dataclass
class ResearchReply:
    text: str


class NotConfigured(Exception):
    pass


class DefaultGeminiResearchService(GeminiService):
    """Gemini research service using google-generativeai SDK."""

    def __init__(self, api_key: Optional[str] = None):
        self._api_key = api_key if api_key is not None else os.getenv("GOOGLE_API_KEY", "")

    async def research(self, query: str) -> str:
        if not self._api_key:
            raise NotConfigured("GOOGLE_API_KEY not set")
        try:
            import google.generativeai as genai

            genai.configure(api_key=self._api_key)
            model = genai.GenerativeModel("gemini-2.0-flash")
            response = await model.generate_content_async(query)
            return response.text
        except ImportError:
            return "Gemini SDK not installed. Run: pip install google-generativeai"
        except Exception as e:
            return f"Gemini research error: {e}"
