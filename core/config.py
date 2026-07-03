"""Runtime configuration and production startup gates."""

from __future__ import annotations

import os
from typing import List

REQUIRED_PROD_SECRETS: tuple[str, ...] = (
    "JWT_SECRET",
    "WC_WEBHOOK_SECRET",
    "LEADS_API_KEY",
)


def require_secrets_enabled() -> bool:
    """True when production secrets must be present and auth must not fail-open."""
    flag = os.getenv("REQUIRE_SECRETS", "").strip().lower()
    if flag in ("1", "true", "yes"):
        return True
    return os.getenv("JADZIA_ENV", "").strip().lower() == "production"


def missing_required_secrets() -> List[str]:
    """Return env var names that are unset or empty."""
    return [name for name in REQUIRED_PROD_SECRETS if not os.getenv(name, "").strip()]


def validate_production_config() -> None:
    """Fail fast on boot when production mode is enabled without required secrets."""
    if not require_secrets_enabled():
        return
    missing = missing_required_secrets()
    if missing:
        raise RuntimeError(
            "Missing required secrets for production: " + ", ".join(missing)
        )
