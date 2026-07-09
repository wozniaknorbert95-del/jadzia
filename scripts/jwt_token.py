"""
Generate a JWT for Worker API / Commander authentication.

Usage (from project root):
  python scripts/jwt_token.py
  python scripts/jwt_token.py --role delegat --sub norbert
  python scripts/jwt_token.py --days 7
"""

import argparse
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if _root.joinpath(".env").exists():
    from dotenv import load_dotenv

    load_dotenv(_root / ".env")

import jwt


def main():
    parser = argparse.ArgumentParser(description="Generate JWT for Worker API")
    parser.add_argument("--days", type=int, default=365, help="Token validity in days")
    parser.add_argument(
        "--role",
        choices=["dowodca", "delegat", "viewer"],
        default="dowodca",
        help="Commander role claim (F3.1)",
    )
    parser.add_argument("--sub", default="worker", help="Subject / user id")
    args = parser.parse_args()

    secret = os.getenv("JWT_SECRET")
    if not secret:
        print("Set JWT_SECRET in environment (e.g. in .env)", file=sys.stderr)
        sys.exit(1)

    payload = {
        "sub": args.sub,
        "role": args.role,
        "exp": datetime.now(timezone.utc) + timedelta(days=args.days),
    }
    token = jwt.encode(payload, secret, algorithm="HS256")
    if isinstance(token, bytes):
        token = token.decode("utf-8")
    print(token)


if __name__ == "__main__":
    main()
