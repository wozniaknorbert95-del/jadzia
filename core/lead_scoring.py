"""Lead scoring service — evaluates customer messages for sales intent."""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional


class LeadScorer:
    """Evaluates customer messages and returns lead score, intent, category, and reason."""

    _HIGH_INTENT_PATTERNS = [
        r"(?:chc[ei]|chcę|chciał[ab]ym|poproszę|zamówi[ćc]|kupi[ćc])",
        r"(?:wycena|wycenę|ile kosztuj|cen[ae]|cennik)",
        r"(?:zamówien|zamawiam|order|bestel)",
        r"(?:termin|kiedy mog|jak szybko|na kiedy)",
        r"(?:fakturacja|faktur[ae]|płatność|płatno[śc]ci)",
        r"(?:projekt|grafika|branding|wrapping|oklejenie)",
    ]

    _MEDIUM_INTENT_PATTERNS = [
        r"(?:oferta|usług[ia]|doradztwo|konsultacja)",
        r"(?:produkt|asortyment|lista)",
        r"(?:pytani[ea]|mam pytanie|chciał[ab]ym się dowiedzie[ćc])",
        r"(?:jak działa|jak to działa|co oferujecie)",
        r"(?:materiał|naklejk[ia]|baner|roll-up|wizytówk[ia])",
    ]

    _LOW_INTENT_PATTERNS = [
        r"(?:dzień dobry|witam|hej|cześć|hi|hello)",
        r"(?:dziękuj[ęe]|thanks|dzięki)",
        r"(?:do widzenia|pa pa|goodbye)",
    ]

    def _compute_score(self, message: str) -> int:
        message_lower = message.lower()
        score = 0

        for pattern in self._HIGH_INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                score += 30

        for pattern in self._MEDIUM_INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                score += 15

        for pattern in self._LOW_INTENT_PATTERNS:
            if re.search(pattern, message_lower):
                score = max(0, score - 5)

        return min(100, max(0, score))

    def _determine_intent(self, score: int) -> str:
        if score >= 60:
            return "high"
        elif score >= 30:
            return "medium"
        return "low"

    def _determine_category(self, message: str, score: int) -> str:
        message_lower = message.lower()
        if re.search(r"(?:reklamacja|zwrot|gwarancja|problem|błąd)", message_lower):
            return "reklamacja"
        if re.search(r"(?:wycena|ile kosztuj|cena|płatno)", message_lower):
            return "wycena"
        if score >= 60:
            return "wycena"
        return "informacja"

    def _determine_reason(self, message: str, score: int) -> str:
        message_lower = message.lower()
        if score >= 60:
            for pattern in self._HIGH_INTENT_PATTERNS:
                if re.search(pattern, message_lower):
                    return f"Wykryto wysoki potencjał zakupowy (score: {score})"
            return f"Wysoki wynik lead scoringu (score: {score})"
        elif score >= 30:
            for pattern in self._MEDIUM_INTENT_PATTERNS:
                if re.search(pattern, message_lower):
                    return f"Zainteresowanie ofertą (score: {score})"
            return f"Średni wynik lead scoringu (score: {score})"
        return f"Niski potencjał zakupowy (score: {score})"

    def compute(
        self,
        user_message: str,
        history: Optional[List[Dict[str, Any]]] = None,
    ) -> Dict[str, Any]:
        """Compute lead score for a customer message.

        Args:
            user_message: The customer's message text.
            history: Optional conversation history for context.

        Returns:
            dict with lead_score, intent, category, reason keys.
        """
        score = self._compute_score(user_message)
        return {
            "lead_score": score,
            "intent": self._determine_intent(score),
            "category": self._determine_category(user_message, score),
            "reason": self._determine_reason(user_message, score),
        }
