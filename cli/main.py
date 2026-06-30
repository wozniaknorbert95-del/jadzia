"""Jadzia CLI — management and diagnostics."""

import argparse
import sys

try:
    import requests
except ImportError:
    print("[ERR] 'requests' is required. Run: pip install requests")
    sys.exit(1)

CLI_VERSION = "1.0.0"


def _get(url: str, timeout: int = 5) -> dict:
    """GET request, return parsed JSON or error."""
    try:
        resp = requests.get(url, timeout=timeout)
        return resp.json() if resp.status_code < 400 else {"error": f"HTTP {resp.status_code}"}
    except requests.RequestException as e:
        return {"error": str(e)}


def cmd_health(url: str) -> int:
    """Check if Jadzia is reachable."""
    data = _get(f"{url}/")
    if data.get("status") == "ok":
        print(f"[OK]  Agent: {data.get('agent', '?')} v{data.get('version', '?')}")
        print(f"      Msg: {data.get('message', '')}")
        return 0
    print(f"[ERR] {data.get('error', 'No response')}")
    return 1


def cmd_status(url: str) -> int:
    """Show current agent session status."""
    data = _get(f"{url}/status")
    if "error" in data:
        print(f"[ERR] {data['error']}")
        return 1
    status = data.get("status", "unknown")
    print(f"[OK]  Session: {status}")
    op = data.get("operation")
    if op:
        print(f"      Task:  {op.get('id', '?')}")
        print(f"      Input: {op.get('user_input', '?')[:60]}")
    return 0


def cmd_version(url: str) -> int:
    """Show CLI and API versions."""
    print(f"  Jadzia CLI:  {CLI_VERSION}")
    data = _get(f"{url}/")
    if "error" not in data:
        print(f"  Jadzia API:  v{data.get('version', '?')}")
        print(f"  Agent:       {data.get('agent', '?')}")
    else:
        print(f"  Jadzia API:  unreachable ({data['error']})")
    return 0


def cmd_test(url: str) -> int:
    """Run quick smoke checks."""
    print(f"Testing {url}...")
    passed, failed = 0, 0

    checks = [
        ("Health", f"{url}/", lambda d: d.get("status") == "ok"),
        ("Worker", f"{url}/worker/health", lambda d: "error" not in d),
        ("Status", f"{url}/status", lambda d: "error" not in d),
    ]

    for name, ep, check in checks:
        data = _get(ep)
        if check(data):
            print(f"  [PASS] {name}")
            passed += 1
        else:
            print(f"  [FAIL] {name}: {data.get('error', 'unexpected')}")
            failed += 1

    print(f"\nResult: {passed}/{passed+failed} passed")
    return 0 if failed == 0 else 1


def cmd_urls(url: str) -> int:
    """Dump all known endpoints (useful for post-migration verification)."""
    endpoints = [
        "/", "/health", "/status", "/worker/health", "/worker/dashboard",
        "/costs", "/sessions",
    ]
    for ep in endpoints:
        data = _get(f"{url}{ep}", timeout=3)
        code_str = ("error" in data and data["error"].startswith("HTTP"))
        val = data.get("error", "OK" if isinstance(data, dict) else "OK")
        print(f"  {ep:30s} {val}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    """Build the CLI argument parser."""
    p = argparse.ArgumentParser(prog="jadzia", description="Jadzia-Core CLI v" + CLI_VERSION)
    p.add_argument("--url", default="http://localhost:8000", help="Jadzia base URL")
    p.add_argument("--quiet", "-q", action="store_true", help="Minimal output")

    def add_url_parser(parser):
        """Add --url flag to a subparser."""
        parser.add_argument("--url", default="http://localhost:8000", help="Jadzia base URL")

    sub = p.add_subparsers(dest="cmd", help="Command")

    s = sub.add_parser("health", help="Quick health check")
    add_url_parser(s)
    s.set_defaults(func=cmd_health)

    s = sub.add_parser("status", help="Session + active task info")
    add_url_parser(s)
    s.set_defaults(func=cmd_status)

    s = sub.add_parser("version", help="CLI + API version")
    add_url_parser(s)
    s.set_defaults(func=cmd_version)

    s = sub.add_parser("test", help="Smoke test suite")
    add_url_parser(s)
    s.set_defaults(func=cmd_test)

    s = sub.add_parser("urls", help="Dump known endpoints")
    add_url_parser(s)
    s.set_defaults(func=cmd_urls)

    return p


def main(argv=None) -> int:
    """CLI entry point."""
    p = build_parser()
    args = p.parse_args(argv)
    if not args.cmd:
        p.print_help()
        return 0

    dispatch = {
        "health": cmd_health,
        "status": cmd_status,
        "version": cmd_version,
        "test": cmd_test,
        "urls": cmd_urls,
    }
    return dispatch[args.cmd](args.url)


if __name__ == "__main__":
    raise SystemExit(main())
