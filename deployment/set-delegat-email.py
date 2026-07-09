#!/usr/bin/env python3
"""One-shot: set Commander delegat_email on VPS. Usage: python3 set-delegat-email.py email@example.com"""
import json
import sys
from pathlib import Path

_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_root))

from agent.commander.settings import update_settings

email = sys.argv[1] if len(sys.argv) > 1 else ""
if not email or "@" not in email:
    print("usage: set-delegat-email.py email@example.com", file=sys.stderr)
    sys.exit(1)

result = update_settings({"delegat_email": email})
print(json.dumps(result, indent=2))
