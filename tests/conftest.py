"""Shared pytest hooks for jadzia-core."""

from __future__ import annotations

import os

# Hermetic test env (8-01): `core.services` calls load_dotenv() at import time,
# so the suite inherits whatever .env the HOST has. On the VPS that is the
# production .env (JWT_SECRET, JADZIA_ENV=production, webhooks, marketing
# HITL...) which flipped tests into prod behavior (401/404/500) that local dev
# never sees. Contract: unit tests run dotenv-free; the flag below is honored
# by core/services.py. Tests that need specific env set it via monkeypatch.
os.environ["JADZIA_TEST_NO_DOTENV"] = "1"

# customer_agent binds `client` at import time; CI runs without .env.
os.environ.setdefault("ANTHROPIC_API_KEY", "sk-ant-test-ci-placeholder")
