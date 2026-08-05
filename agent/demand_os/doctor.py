"""Demand OS doctor — local integrity for PROGRAM SEAL (no network)."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.content_calendar import DEFAULT_CALENDAR_PATH
from agent.demand_os.marketing_mode import resolve_marketing_mode
from agent.demand_os.observability import money_check


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


REQUIRED_MODULES = [
    "agent/demand_os/starts_ingest.py",
    "agent/demand_os/publish_gate_bridge.py",
    "agent/demand_os/ga4_adapter.py",
    "agent/demand_os/gdrive_cf.py",
    "agent/demand_os/widget_leads.py",
    "agent/demand_os/db_utm.py",
    "agent/demand_os/ledger.py",
    "agent/demand_os/stl_monitor.py",
    "agent/demand_os/week_ritual.py",
    "agent/demand_os/audit_log.py",
    "agent/demand_os/design_wizard.py",
    "agent/demand_os/content_factory.py",
    "agent/demand_os/weekly_tune.py",
    "agent/demand_os/observability.py",
    "agent/demand_os/a2a_bus.py",
    "agent/demand_os/memory.py",
    "agent/demand_os/agents/wave1.py",
    "agent/demand_os/agents/wave2.py",
    "agent/demand_os/agents/wave3.py",
    "agent/demand_os/rbac.py",
    "agent/demand_os/fatigue.py",
    "agent/demand_os/desk_contract.py",
    "agent/demand_os/hitl_decision.py",
    "docs/ops/demand-os/DESK-CONTRACT.md",
    "docs/ops/demand-os/HITL-READY-TOOL.md",
    "tools/demand_os_hub.py",
    "tools/demand_os_mcp.py",
    "tools/demand_os_agents.py",
    "docs/ops/demand-os/CALENDAR-SOT.md",
    "docs/ops/demand-os/TOOL-PASS.md",
    "docs/ops/demand-os/MASTER-STAGES-RESIDUAL.md",
    "docs/ops/demand-os/PROGRAM-PHASES.md",
    "docs/ops/demand-os/OS-TARGET-COHERENCE.md",
]

TIP_FILES = [
    "docs/ops/demand-os/STATE.md",
    "docs/ops/marketing/OPERATOR-TODAY.md",
]


@dataclass
class DoctorReport:
    ok: bool
    checks: List[Dict[str, Any]] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)
    marketing: str = "PARKED_LAST"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _check(name: str, ok: bool, detail: str = "") -> Dict[str, Any]:
    return {"name": name, "ok": ok, "detail": detail}


def _is_tool_first_state(text: str) -> bool:
    """TOOL FIRST era: live cadence PARKED while tool residual is active."""
    upper = text.upper()
    has_tool = "TOOL FIRST" in upper or "TOOL 100%" in upper
    has_park = "PARKED" in upper and (
        "LIVE P0" in upper
        or "4-P0" in upper
        or "CADENCE PARKED" in upper
        or "PUBLISH CADENCE PARKED" in upper
        or "LIVE PUBLISH CADENCE PARKED" in upper
    )
    return has_tool and has_park


def _state_marketing_pair(text: str) -> tuple[str, str] | None:
    """Return coherent (marketing, gate) markers from STATE tip text."""
    has_hitl = "HITL_LIVE" in text
    has_parked_mode = "PARKED_LAST" in text
    has_ready = "READY" in text
    has_blocked = "BLOCKED" in text

    # Reject crossed historical pairs (HITL_LIVE+BLOCKED without READY, etc.)
    if has_hitl and has_ready and not has_blocked:
        return "HITL_LIVE", "READY"
    if has_parked_mode and has_blocked and not has_ready:
        return "PARKED_LAST", "BLOCKED"
    if has_hitl and has_blocked and not has_ready:
        return None
    if has_parked_mode and has_ready and not has_blocked:
        return None
    if _is_tool_first_state(text):
        return "HITL_LIVE", "PARKED"
    return None


def _tip_ok(*, rel: str, text: str) -> tuple[bool, str]:
    if rel.endswith("STATE.md"):
        if _is_tool_first_state(text):
            return True, "TOOL_FIRST/PARKED"
        pair = _state_marketing_pair(text)
        ok = pair is not None and (
            "TOOL-INTEGRITY-SEAL" in text or "TOOL FIRST" in text.upper()
        )
        detail = f"{pair[0]}/{pair[1]}" if ok and pair else "state tip mismatch"
        return ok, detail

    if rel.endswith("OPERATOR-TODAY.md"):
        lower = text.lower()
        has_order = "tool 100%" in lower or "tool first" in lower
        has_focus = (
            "tool-integrity seal" in lower
            or "execution freeze" in lower
            or "live p0" in lower
            or "parked" in lower
        )
        ok = has_order and has_focus
        detail = "tool-first seal" if ok else "operator tip mismatch"
        return ok, detail

    return False, "missing"


def run_doctor(*, root: Optional[Path] = None) -> DoctorReport:
    repo = root or _repo_root()
    checks: List[Dict[str, Any]] = []
    errors: List[str] = []

    # Phase0
    phase0 = repo / "tools" / "demand_os_phase0_check.py"
    if phase0.is_file():
        try:
            proc = subprocess.run(
                [sys.executable, str(phase0)],
                cwd=str(repo),
                capture_output=True,
                text=True,
                timeout=60,
                env={**os.environ, "PYTHONPATH": str(repo)},
            )
            p0_ok = proc.returncode == 0 and "Phase 0 CHECK: PASS" in (proc.stdout or "")
            out = (proc.stdout or "") + (proc.stderr or "")
            # Must not push organic HITL as next
            organic_drift = "organic HITL" in out and "PARKED_LAST" not in out
            if organic_drift:
                p0_ok = False
                errors.append("phase0 tip still says organic HITL next")
            checks.append(_check("phase0", p0_ok, out.strip().splitlines()[-1] if out.strip() else ""))
            if not p0_ok and "phase0 tip" not in " ".join(errors):
                errors.append("phase0 FAIL")
        except Exception as exc:
            checks.append(_check("phase0", False, str(exc)[:200]))
            errors.append(f"phase0 exception: {exc}")
    else:
        checks.append(_check("phase0", False, "missing phase0 script"))
        errors.append("missing phase0")

    # Required files
    missing = [p for p in REQUIRED_MODULES if not (repo / p).is_file()]
    checks.append(
        _check(
            "required_files",
            not missing,
            f"missing={missing}" if missing else f"count={len(REQUIRED_MODULES)}",
        )
    )
    if missing:
        errors.append(f"missing modules: {missing}")

    # TT transport symbol
    transport = (repo / "agent/demand_os/connectors/transport.py").read_text(encoding="utf-8")
    tt_ok = "class LiveTikTokTransport" in transport
    checks.append(_check("tt_transport", tt_ok, "LiveTikTokTransport"))
    if not tt_ok:
        errors.append("LiveTikTokTransport missing")

    # Calendar SoT = JSON
    cal_ok = DEFAULT_CALENDAR_PATH.name == "CONTENT-CALENDAR.json"
    checks.append(_check("calendar_sot_json", cal_ok, str(DEFAULT_CALENDAR_PATH.name)))
    if not cal_ok:
        errors.append("calendar SoT not JSON")

    # Money check readable
    try:
        mc = money_check()
        mc_ok = "starts_utm" in mc and mc.get("kill_vanity") is True
        checks.append(
            _check(
                "money_check",
                mc_ok,
                f"starts_utm={mc.get('starts_utm')} top_hook={mc.get('top_hook')}",
            )
        )
        if not mc_ok:
            errors.append("money_check shape FAIL")
    except Exception as exc:
        checks.append(_check("money_check", False, str(exc)[:200]))
        errors.append(f"money_check: {exc}")

    # Marketing tips must be semantically coherent with current mode
    for rel in TIP_FILES:
        path = repo / rel
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        tip_ok, detail = _tip_ok(rel=rel, text=text)
        checks.append(_check(f"tip:{rel}", path.is_file() and tip_ok, detail if path.is_file() else "missing"))
        if not tip_ok:
            errors.append(f"tip mismatch for marketing mode: {rel}")

    # No organic ACTIVE drift in STATE
    state = repo / "docs/ops/demand-os/STATE.md"
    if state.is_file():
        st = state.read_text(encoding="utf-8")
        drift = "organic sprint ACTIVE" in st.lower() or "GO ORGANIC RESUME" in st
        checks.append(_check("state_no_organic_active", not drift, "clean" if not drift else "drift"))
        if drift:
            errors.append("STATE organic ACTIVE drift")

    # Coherence: R9 + GDrive honesty + phases tip
    try:
        from agent.demand_os.validator import RULE_R9_DECOY_MENU, ALL_RULES

        r9_ok = RULE_R9_DECOY_MENU in ALL_RULES
        checks.append(_check("validator_r9_decoy", r9_ok, RULE_R9_DECOY_MENU))
        if not r9_ok:
            errors.append("R9 decoy missing")
    except Exception as exc:
        checks.append(_check("validator_r9_decoy", False, str(exc)[:120]))
        errors.append("R9 import fail")

    try:
        from agent.demand_os.gdrive_cf import list_cf_assets

        gd = list_cf_assets(limit=2)
        gd_ok = gd.get("mode") == "local_registry" and gd.get("ok") is True
        checks.append(_check("gdrive_local_registry", gd_ok, gd.get("mode") or ""))
        if not gd_ok:
            errors.append("gdrive not local_registry")
    except Exception as exc:
        checks.append(_check("gdrive_local_registry", False, str(exc)[:120]))
        errors.append("gdrive check fail")

    phases = repo / "docs/ops/demand-os/PROGRAM-PHASES.md"
    ph_ok = phases.is_file() and "ETAP 1" in phases.read_text(encoding="utf-8")
    checks.append(_check("program_phases", ph_ok, "PROGRAM-PHASES.md"))
    if not ph_ok:
        errors.append("PROGRAM-PHASES missing")

    try:
        from agent.commander.constants import ROLE_SCOPES

        scopes = ROLE_SCOPES.get("delegat") or []
        rbac_ok = "demand_os:read" in scopes and "demand_os:act" in scopes
        checks.append(_check("rbac_demand_os_scopes", rbac_ok, "delegat scopes"))
        if not rbac_ok:
            errors.append("demand_os scopes missing on delegat")
    except Exception as exc:
        checks.append(_check("rbac_demand_os_scopes", False, str(exc)[:120]))
        errors.append("rbac check fail")

    # Desk v2.1.1 contract on status payload
    try:
        from agent.demand_os.commander_status import build_demand_os_status
        from agent.demand_os.desk_contract import CONTRACT_TOP_KEYS

        st = build_demand_os_status()
        required = (
            "robota_dnia",
            "icp_role_week",
            "iso_week",
            "state",
            "week_calendar",
            "shells_line",
            "dual_cash",
            "data_mode",
            "last_real_event",
            "footer",
            "kpi",
            "screen",
            "diagnostics",
            "contract_version",
        )
        missing_k = [k for k in required if k not in st]
        hunt = (st.get("screen") or {}).get("hunt_queue") or []
        hunt_ok = isinstance(hunt, list) and (
            not hunt or all("action" in h for h in hunt)
        )
        footer = st.get("footer") or {}
        desk_ok = (
            st.get("desk") == "Demand Desk v2.1"
            and st.get("gate") == "DEMAND-OS-DESK-CONTRACT-00"
            and not missing_k
            and hunt_ok
            and "wizard_starts_wow_delta" in (st.get("kpi") or {})
            and "go_ready" not in st
            and isinstance((st.get("diagnostics") or {}).get("go_ready"), dict)
            and isinstance(footer.get("doctor_ok"), bool)
            and isinstance(st.get("week_calendar"), list)
            and len(st.get("week_calendar") or []) >= 5
            and CONTRACT_TOP_KEYS.issubset(set(st.keys()))
        )
        checks.append(
            _check(
                "desk_contract_v21",
                desk_ok,
                f"missing={missing_k}" if missing_k else "v2.1.1 ok",
            )
        )
        if not desk_ok:
            errors.append("desk_contract_v21 FAIL")
    except Exception as exc:
        checks.append(_check("desk_contract_v21", False, str(exc)[:160]))
        errors.append(f"desk_contract: {exc}")

    # S1: doctor surfaces worker-loop health (alias of wave-check staleness) —
    # an owner running `doctor` should see a dead/stale worker without knowing
    # the wave-check exists. Severity is env-aware: ADVISORY by default (dev
    # machines have no worker loop — failing doctor there would be crying
    # wolf). On prod, where the worker timer is LIVE, the service env sets
    # DEMAND_OS_STALENESS_BLOCKING=1 and staleness becomes a hard gate.
    staleness_blocking = os.environ.get("DEMAND_OS_STALENESS_BLOCKING") == "1"
    try:
        from agent.demand_os.agents.wave_check import _heartbeat_staleness_check

        stale = _heartbeat_staleness_check()
        detail = stale["detail"] + (
            " [blocking]" if staleness_blocking else " [advisory]"
        )
        checks.append(_check("agents_staleness", bool(stale["ok"]), detail))
        if staleness_blocking and not stale["ok"]:
            errors.append("agents_staleness FAIL (blocking mode)")
    except Exception as exc:
        checks.append(_check("agents_staleness", False, str(exc)[:160]))
        if staleness_blocking:
            errors.append("agents_staleness error (blocking mode)")

    # 9-06 OPT-B: worker failure sink — systemd OnFailure alert unit appends to
    # ALERTS.jsonl at crash time; doctor surfaces it through the same path and
    # the same severity flag as staleness (advisory dev / blocking prod).
    try:
        from agent.demand_os.agents.alerts import active_alerts

        act = active_alerts()
        detail = (
            "no active worker failures"
            if not act
            else f"{len(act)} failure(s) <24h, last={act[-1].get('ts')}"
        )
        detail += " [blocking]" if staleness_blocking else " [advisory]"
        checks.append(_check("worker_failures", not act, detail))
        if staleness_blocking and act:
            errors.append("worker_failures FAIL (blocking mode)")
    except Exception as exc:
        checks.append(_check("worker_failures", False, str(exc)[:160]))
        if staleness_blocking:
            errors.append("worker_failures error (blocking mode)")

    _ADVISORY = set() if staleness_blocking else {"agents_staleness", "worker_failures"}
    ok = not errors and all(c["ok"] for c in checks if c["name"] not in _ADVISORY)
    state_text = (
        (repo / "docs/ops/demand-os/STATE.md").read_text(encoding="utf-8")
        if (repo / "docs/ops/demand-os/STATE.md").is_file()
        else ""
    )
    # Report env/mode truth; TOOL FIRST tip may say PARKED cadence while env=GO → HITL_LIVE
    marketing = resolve_marketing_mode()
    if marketing == "PARKED_LAST":
        state_pair = _state_marketing_pair(state_text)
        if state_pair and state_pair[0] == "PARKED_LAST":
            marketing = "PARKED_LAST"
    return DoctorReport(ok=ok, checks=checks, errors=errors, marketing=marketing)
