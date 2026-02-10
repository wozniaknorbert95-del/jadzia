"""
Klasyfikacja intencji użytkownika (APPROVAL / REJECTION / NEW_TASK / UNCLEAR).
"""

import json
import logging
from typing import Optional

_log = logging.getLogger(__name__)

from ..state import load_state, get_pending_plan, get_current_status
from ..prompt import get_intent_classifier_prompt


async def classify_intent(
    user_input: str,
    chat_id: str,
    source: str,
    call_claude,
    task_id: Optional[str] = None,
) -> str:
    """Klasyfikacja intencji: APPROVAL / REJECTION / NEW_TASK / MODIFICATION / UNCLEAR"""
    try:
        status = get_current_status(chat_id, source, task_id=task_id) or "idle"
        has_pending = get_pending_plan(chat_id, source, task_id=task_id) is not None
        recent_history = "Brak historii"

        prompt = get_intent_classifier_prompt(
            user_message=user_input,
            status=status,
            has_pending_plan=has_pending,
            recent_history=recent_history
        )

        response = await call_claude(
            messages=[{"role": "user", "content": prompt}],
            task_complexity="simple"
        )

        result = json.loads(response)
        intent = result.get("intent", "UNCLEAR")
        confidence = result.get("confidence", 0.5)
        _log.debug("[INTENT] %s (confidence: %s) - %s", intent, confidence, result.get("reasoning", ""))
        return intent

    except Exception as e:
        _log.warning("[INTENT] %s - fallback to keyword matching", e)
        lower = user_input.lower()

        if get_pending_plan(chat_id, source, task_id=task_id):
            approval_kw = ["tak", "ok", "yes", "rób", "wdróż", "wykonaj", "dawaj"]
            if any(kw in lower for kw in approval_kw):
                return "APPROVAL"

            rejection_kw = ["nie", "no", "stop", "anuluj", "wycofaj"]
            if any(kw in lower for kw in rejection_kw):
                return "REJECTION"

        return "NEW_TASK"
