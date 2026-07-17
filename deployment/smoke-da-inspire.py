#!/usr/bin/env python3
"""Post-deploy smoke for Design Agent / INSPIRE routes (no secrets)."""
from __future__ import annotations

import json
import subprocess
import sys


def main() -> int:
    from agent.inspire import engine  # noqa: F401
    from agent.inspire.creative_director import produce_layout_specs  # noqa: F401
    from agent.inspire.overlay_renderer import apply_overlay  # noqa: F401

    print("import_ok")

    out = subprocess.check_output(
        ["curl", "-sf", "http://localhost:8000/openapi.json"],
        text=True,
    )
    paths = list(json.loads(out)["paths"].keys())
    da = sorted(k for k in paths if "design-agent" in k)
    for p in da:
        print("route", p)
    print("COUNT", len(da))

    # Accept either spelling present in openapi (inspiration vs inspire).
    has_msg = any("intake/message" in p or ("inspir" in p and "message" in p) for p in da)
    has_render = any("mockups/render" in p for p in da)
    has_generate = any(p.endswith("/generate") or p.endswith("design-agent/generate") for p in da)
    has_opening = any("chat/opening" in p for p in da)
    if not (has_msg and has_render and has_generate and has_opening and len(da) >= 8):
        print(
            "FAIL checks",
            {
                "has_msg": has_msg,
                "has_render": has_render,
                "has_generate": has_generate,
                "has_opening": has_opening,
                "count": len(da),
            },
        )
        return 1
    print("SMOKE_PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
