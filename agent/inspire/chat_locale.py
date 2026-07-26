"""Resolve chat locale + error strings from inspire brain packs (with NL fallback)."""

from __future__ import annotations

import logging
import os
from functools import lru_cache
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

DEFAULT_LOCALE = "nl-NL"
SUPPORTED = ("nl-NL", "pl-PL", "en-GB")
_ALIASES = {
    "nl": "nl-NL",
    "nl-nl": "nl-NL",
    "pl": "pl-PL",
    "pl-pl": "pl-PL",
    "en": "en-GB",
    "en-gb": "en-GB",
    "en-us": "en-GB",
}

_FALLBACK_ERRORS = {
    "empty_message": {
        "nl-NL": "Bericht mag niet leeg zijn.",
        "pl-PL": "Wiadomość nie może być pusta.",
        "en-GB": "Message must not be empty.",
    },
    "rate_limit_chat": {
        "nl-NL": "Te veel chatberichten. Probeer het over een uur opnieuw.",
        "pl-PL": "Zbyt wiele wiadomości. Spróbuj ponownie później.",
        "en-GB": "Too many chat messages. Please try again later.",
    },
    "rate_limit_generate": {
        "nl-NL": (
            "Je hebt al 2 mock-ups gegenereerd vanaf dit netwerk. "
            "Wacht een uur of neem contact op via flexgrafik.nl."
        ),
        "pl-PL": (
            "Wygenerowano już 2 mockupy z tej sieci. "
            "Poczekaj godzinę lub skontaktuj się przez flexgrafik.nl."
        ),
        "en-GB": (
            "You already generated 2 mock-ups from this network. "
            "Wait an hour or contact us via flexgrafik.nl."
        ),
    },
    "session_not_found": {
        "nl-NL": "Sessie niet gevonden of verlopen.",
        "pl-PL": "Nie znaleziono sesji lub wygasła.",
        "en-GB": "Session not found or expired.",
    },
    "logo_received": {
        "nl-NL": "Logo ontvangen.",
        "pl-PL": "Logo otrzymane.",
        "en-GB": "Logo received.",
    },
}


def normalize_locale(locale: str | None) -> str:
    if not locale:
        return DEFAULT_LOCALE
    raw = str(locale).strip()
    if raw in SUPPORTED:
        return raw
    return _ALIASES.get(raw.lower(), DEFAULT_LOCALE)


def _ensure_inspire_path() -> Path:
    repo = Path(os.getenv("INSPIRE_REPO_PATH", "/opt/inspire"))
    import sys

    if str(repo) not in sys.path:
        sys.path.insert(0, str(repo))
    return repo


@lru_cache(maxsize=8)
def _load_pack(locale: str) -> dict[str, Any]:
    loc = normalize_locale(locale)
    try:
        _ensure_inspire_path()
        from engine.v4.intake.intake_copy import load_chat_pack

        return load_chat_pack(loc)
    except Exception as exc:  # noqa: BLE001
        logger.debug("chat locale pack unavailable (%s): %s", loc, exc)
        return {}


def error_message(key: str, locale: str | None = None) -> str:
    loc = normalize_locale(locale)
    pack = _load_pack(loc)
    errors = pack.get("errors") or {}
    if key in errors and errors[key]:
        return str(errors[key])
    # logo_received lives in acks in brain packs
    if key == "logo_received":
        acks = pack.get("acks") or {}
        # first line of logo_boilerplate is "Logo ontvangen — …"
        if acks.get("logo_boilerplate"):
            return str(acks["logo_boilerplate"]).split("\n")[0].split("—")[0].strip().rstrip(".")
        return _FALLBACK_ERRORS["logo_received"][loc]
    return _FALLBACK_ERRORS.get(key, {}).get(loc) or _FALLBACK_ERRORS.get(key, {}).get(DEFAULT_LOCALE, key)
