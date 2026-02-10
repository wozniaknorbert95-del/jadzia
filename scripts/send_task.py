#!/usr/bin/env python3
"""
Wyślij zadanie do Worker API (localhost). Do uruchomienia na VPS w katalogu projektu.

Użycie:
  cd /root/jadzia
  python3 scripts/send_task.py "Przywróć na stronie custom header i menu – zniknęło."
  python3 scripts/send_task.py "Treść zadania" --chat_id telegram_123456
  python3 scripts/send_task.py "Treść" --poll   # czeka aż task się skończy (completed/failed)

Na Debianie/Ubuntu: python3 (nie python). Na VPS uruchamiaj z venv projektu,
żeby były httpx/jwt:  ./venv/bin/python3 scripts/send_task.py "..." 
Wymaga: JWT_SECRET (lub TELEGRAM_BOT_JWT_TOKEN) w .env lub w env. Worker API: 127.0.0.1:8000.
"""

import argparse
import json
import os
import sys
import time
from pathlib import Path

_root = Path(__file__).resolve().parent.parent
if _root.joinpath(".env").exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_root / ".env")
    except ImportError:
        pass  # bez python-dotenv: używaj zmiennych z otoczenia (systemd, export)

import httpx

BASE_URL = os.getenv("TELEGRAM_BOT_API_BASE_URL", "http://127.0.0.1:8000").strip() or "http://127.0.0.1:8000"
TIMEOUT = 120.0


def get_jwt() -> str:
    token = os.getenv("TELEGRAM_BOT_JWT_TOKEN", "").strip()
    if token:
        return token
    secret = os.getenv("JWT_SECRET", "").strip()
    if not secret:
        print("Ustaw JWT_SECRET lub TELEGRAM_BOT_JWT_TOKEN w .env", file=sys.stderr)
        sys.exit(1)
    try:
        import jwt
        from datetime import datetime, timedelta, timezone
        payload = {"sub": "worker", "exp": datetime.now(timezone.utc) + timedelta(days=365)}
        t = jwt.encode(payload, secret, algorithm="HS256")
        return t if isinstance(t, str) else t.decode("utf-8")
    except Exception as e:
        print(f"JWT error: {e}", file=sys.stderr)
        sys.exit(1)


def main():
    ap = argparse.ArgumentParser(description="Wyślij zadanie do Jadzia Worker API")
    ap.add_argument("instruction", nargs="?", default="", help="Treść zadania (lub podaj w cudzysłowie)")
    ap.add_argument("--chat_id", default="telegram_cli", help="chat_id sesji (default: telegram_cli)")
    ap.add_argument("--test_mode", action="store_true", help="test_mode (auto-approve)")
    ap.add_argument("--dry_run", action="store_true", help="dry_run (preview)")
    ap.add_argument("--poll", action="store_true", help="Czekaj aż status będzie completed/failed")
    ap.add_argument("--poll_interval", type=float, default=5.0, help="Co ile sekund sprawdzać status (default: 5)")
    args = ap.parse_args()

    instruction = (args.instruction or "").strip()
    if not instruction:
        print("Podaj treść zadania, np.: python scripts/send_task.py \"Przywróć header i menu\"", file=sys.stderr)
        sys.exit(1)

    jwt_token = get_jwt()
    url = BASE_URL.rstrip("/") + "/worker/task"
    headers = {"Authorization": f"Bearer {jwt_token}", "Content-Type": "application/json"}
    payload = {
        "instruction": instruction,
        "chat_id": args.chat_id,
        "test_mode": args.test_mode,
    }
    params = {"dry_run": str(args.dry_run).lower()}

    try:
        with httpx.Client(timeout=TIMEOUT) as client:
            r = client.post(url, json=payload, headers=headers, params=params)
            r.raise_for_status()
            data = r.json()
    except httpx.HTTPStatusError as e:
        print(f"HTTP {e.response.status_code}: {e.response.text}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Błąd: {e}", file=sys.stderr)
        sys.exit(1)

    task_id = data.get("task_id", "")
    status = data.get("status", "")
    pos = data.get("position_in_queue", 0)
    print(f"task_id={task_id} status={status} position_in_queue={pos}")

    if not args.poll:
        print("Worker loop przetworzy zadanie w tle. Status: GET /worker/task/" + task_id)
        return

    # Poll until terminal
    get_url = BASE_URL.rstrip("/") + f"/worker/task/{task_id}"
    while True:
        time.sleep(args.poll_interval)
        try:
            with httpx.Client(timeout=30.0) as client:
                r = client.get(get_url, headers={"Authorization": f"Bearer {jwt_token}"})
                r.raise_for_status()
                info = r.json()
        except Exception as e:
            print(f"Poll error: {e}", file=sys.stderr)
            continue
        s = info.get("status", "")
        print(f"  status={s}")
        if s in ("completed", "failed"):
            if "response" in info:
                print("response:", (info.get("response") or "")[:500])
            break


if __name__ == "__main__":
    main()
