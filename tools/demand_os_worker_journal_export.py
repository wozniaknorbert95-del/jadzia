#!/usr/bin/env python3
"""Demand OS worker journal → evidence snapshot (9-03).

Pulls `journalctl -u demand-os-agents-worker.service` and renders a markdown
report into docs/handoffs/evidence/worker/: tick count, dispatch stats per
role/action, errors, plus the raw journal tail. Run on the VPS (journalctl
required); the parser is pure and unit-tested locally.

Usage (VPS):
    venv/bin/python tools/demand_os_worker_journal_export.py --since "7 days ago"
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parents[1]
UNIT = "demand-os-agents-worker.service"

_PREFIX = re.compile(r"^\d{4}-\d{2}-\d{2}T\S+ \S+ [^:]+\[\d+\]: (.*)$")
# systemd logs "Starting <unit> - <description>..." for oneshot units (and
# "Started ..." for others) — accept both, name or description.
_STARTED = re.compile(r"Start(?:ing|ed) .*(?:demand-os-agents-worker|Demand OS agents worker)")
_FAILED = re.compile(r"demand-os-agents-worker\.service: Failed")


def _strip_prefix(line: str) -> str:
    m = _PREFIX.match(line)
    return m.group(1) if m else line


def parse_journal(text: str) -> Dict[str, Any]:
    """Extract run-due envelopes + tick stats from journalctl text."""
    ticks = len(_STARTED.findall(text))
    failures = len(_FAILED.findall(text))
    envelopes: List[Dict[str, Any]] = []
    buf: List[str] = []
    depth = 0
    for raw in text.splitlines():
        line = _strip_prefix(raw)
        if depth == 0:
            idx = line.find("{")
            if idx == -1:
                continue
            line = line[idx:]
        buf.append(line)
        depth += line.count("{") - line.count("}")
        if depth <= 0 and buf:
            blob = "\n".join(buf)
            buf = []
            depth = 0
            try:
                data = json.loads(blob)
            except json.JSONDecodeError:
                continue
            if isinstance(data, dict) and "runs" in data and "dispatched" in data:
                envelopes.append(data)

    per_role: Dict[str, Dict[str, int]] = {}
    error_lines: List[str] = []
    for env in envelopes:
        for r in env.get("runs", []):
            key = f"{r.get('role')}/{r.get('action')}"
            bucket = per_role.setdefault(key, {"dispatched": 0, "error": 0, "dry_run": 0})
            status = str(r.get("status"))
            if status in bucket:
                bucket[status] += 1
            if status == "error":
                error_lines.append(f"{key}: {str(r.get('error', ''))[:120]}")

    return {
        "ticks": ticks,
        "service_failures": failures,
        "envelopes": envelopes and len(envelopes) or 0,
        "dispatched_total": sum(int(e.get("dispatched", 0)) for e in envelopes),
        "errors_total": sum(int(e.get("errors", 0)) for e in envelopes),
        "per_role": per_role,
        "error_lines": error_lines[:20],
    }


def render_markdown(
    stats: Dict[str, Any], raw_tail: str, *, since: str, host: str, unit: str = UNIT
) -> str:
    rows = "\n".join(
        f"| {key} | {v['dispatched']} | {v['error']} | {v['dry_run']} |"
        for key, v in sorted(stats["per_role"].items())
    ) or "| — | 0 | 0 | 0 |"
    errors = (
        "\n".join(f"- `{e}`" for e in stats["error_lines"]) or "- brak"
    )
    return f"""# Worker journal evidence — {datetime.now(timezone.utc).date().isoformat()}

- host: `{host}` · unit: `{unit}` · since: `{since}`
- wygenerowano: {datetime.now(timezone.utc).isoformat(timespec="seconds")} przez `tools/demand_os_worker_journal_export.py`

## Summary

| Metryka | Wartość |
|---------|---------|
| ticków (Started) | {stats['ticks']} |
| service failures | {stats['service_failures']} |
| run-due envelopes | {stats['envelopes']} |
| dispatched total | {stats['dispatched_total']} |
| errors total | {stats['errors_total']} |

## Per role/action

| role/action | dispatched | error | dry_run |
|-------------|-----------|-------|---------|
{rows}

## Error lines (max 20)

{errors}

## Raw tail

```text
{raw_tail.rstrip()}
```
"""


def main(argv: List[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--since", default="7 days ago", help="journalctl --since argument")
    ap.add_argument("--unit", default=UNIT)
    ap.add_argument("--tail", type=int, default=150, help="raw journal tail lines in report")
    ap.add_argument("--out-dir", default=str(ROOT / "docs" / "handoffs" / "evidence" / "worker"))
    args = ap.parse_args(argv)

    proc = subprocess.run(
        ["journalctl", "-u", args.unit, "--since", args.since, "--no-pager", "-o", "short-iso"],
        capture_output=True,
        text=True,
        timeout=120,
    )
    if proc.returncode != 0:
        print(f"journalctl failed (rc={proc.returncode}): {proc.stderr[:300]}", file=sys.stderr)
        return 2
    raw = proc.stdout
    stats = parse_journal(raw)
    host = subprocess.run(["hostname"], capture_output=True, text=True).stdout.strip() or "unknown"
    tail_lines = raw.splitlines()[-args.tail :]
    md = render_markdown(stats, "\n".join(tail_lines), since=args.since, host=host, unit=args.unit)

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    out = out_dir / f"worker-journal-{datetime.now(timezone.utc).date().isoformat()}.md"
    out.write_text(md, encoding="utf-8")
    print(json.dumps({"ok": True, "out": str(out), "stats": stats}, ensure_ascii=False, indent=1))
    return 0


if __name__ == "__main__":
    sys.exit(main())
