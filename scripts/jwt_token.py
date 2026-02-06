"""
Generate a JWT for Worker API authentication.

Usage (from project root):
  python scripts/jwt_token.py
  python scripts/jwt_token.py --days 7

Requires JWT_SECRET in environment (e.g. from .env in project root).
Output: token on stdout for use as Authorization: Bearer <token>.
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

# Load .env from project root
_root = Path(__file__).resolve().parent.parent
if _root.joinpath(".env").exists():
    from dotenv import load_dotenv
    load_dotenv(_root / ".env")

import jwt


def main():
    parser = argparse.ArgumentParser(description="Generate JWT for Worker API")
    parser.add_argument(
        "--days",
        type=int,
        default=365,
        help="Token validity in days (default: 365)",
    )
    args = parser.parse_args()

    secret = os.getenv("JWT_SECRET")
    if not secret:
        print("Set JWT_SECRET in environment (e.g. in .env)", file=sys.stderr)
        sys.exit(1)

    payload = {
        "sub": "worker",
        "exp": datetime.now(timezone.utc) + timedelta(days=args.days),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    print(token)


if __name__ == "__main__":
    main()
