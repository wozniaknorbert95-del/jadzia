#!/usr/bin/env python3
"""Demand OS F4 CLI — Blog ICP pipeline (C.4 → Val C.5)."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from agent.demand_os.blog_pipeline import (
    ALLOWED_ICP_ROLES,
    BlogPipelineError,
    generate_article,
    list_drafts,
    persist_article,
    run_pipeline,
    validate_article,
)


def cmd_roles(_: argparse.Namespace) -> int:
    print(json.dumps(sorted(ALLOWED_ICP_ROLES), indent=2))
    return 0


def cmd_generate(args: argparse.Namespace) -> int:
    try:
        article = generate_article(
            args.role, asset_id=args.asset_id, angle=args.angle
        )
    except BlogPipelineError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    if args.persist:
        path = persist_article(article)
        print(
            json.dumps(
                {"ok": True, "article": article.to_dict(), "path": str(path)},
                ensure_ascii=False,
                indent=2,
            )
        )
    else:
        print(json.dumps({"ok": True, "article": article.to_dict()}, ensure_ascii=False, indent=2))
    return 0


def cmd_validate(args: argparse.Namespace) -> int:
    try:
        article = generate_article(
            args.role, asset_id=args.asset_id, angle=args.angle
        )
        article, decision = validate_article(
            article, log=not args.no_log, emit_events=False
        )
    except BlogPipelineError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(
        json.dumps(
            {"article": article.to_dict(), "decision": decision.to_dict()},
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0 if decision.ok else 1


def cmd_pipeline(args: argparse.Namespace) -> int:
    try:
        result = run_pipeline(
            args.role,
            asset_id=args.asset_id,
            angle=args.angle,
            persist=not args.no_persist,
            calendar=not args.no_calendar,
            log=not args.no_log,
            emit_events=False,
        )
    except BlogPipelineError as exc:
        print(json.dumps({"ok": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    ok = result["decision"]["decision"] == "PASS"
    print(json.dumps({"ok": ok, **result}, ensure_ascii=False, indent=2))
    return 0 if ok else 1


def cmd_list(_: argparse.Namespace) -> int:
    print(json.dumps(list_drafts(), ensure_ascii=False, indent=2))
    return 0


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(description="Demand OS F4 — Blog ICP pipeline")
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("roles", help="List allowed ICP roles").set_defaults(func=cmd_roles)

    g = sub.add_parser("generate", help="Generate ICP blog draft (no Val)")
    g.add_argument("--role", required=True)
    g.add_argument("--asset-id", default=None)
    g.add_argument("--angle", default=None)
    g.add_argument("--persist", action="store_true")
    g.set_defaults(func=cmd_generate)

    v = sub.add_parser("validate", help="Generate + run Sniper Validator C.5")
    v.add_argument("--role", required=True)
    v.add_argument("--asset-id", default=None)
    v.add_argument("--angle", default=None)
    v.add_argument("--no-log", action="store_true")
    v.set_defaults(func=cmd_validate)

    pipe = sub.add_parser("pipeline", help="Generate → Val → persist → calendar")
    pipe.add_argument("--role", required=True)
    pipe.add_argument("--asset-id", default=None)
    pipe.add_argument("--angle", default=None)
    pipe.add_argument("--no-persist", action="store_true")
    pipe.add_argument("--no-calendar", action="store_true")
    pipe.add_argument("--no-log", action="store_true")
    pipe.set_defaults(func=cmd_pipeline)

    sub.add_parser("list", help="List persisted blog drafts").set_defaults(func=cmd_list)

    args = p.parse_args(argv)
    return int(args.func(args))


if __name__ == "__main__":
    sys.exit(main())
