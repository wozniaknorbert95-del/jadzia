"""Demand OS doctor — local integrity for PROGRAM SEAL (no network)."""

from __future__ import annotations

import os
import subprocess
import sys
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.content_calendar import DEFAULT_CALENDAR_PATH
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

TIP_FILES_PARKED = [
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

    # Marketing PARKED_LAST in tip files
    for rel in TIP_FILES_PARKED:
        path = repo / rel
        text = path.read_text(encoding="utf-8") if path.is_file() else ""
        tip_ok = path.is_file() and "PARKED_LAST" in text
        checks.append(_check(f"tip:{rel}", tip_ok, "PARKED_LAST" if tip_ok else "missing"))
        if not tip_ok:
            errors.append(f"tip missing PARKED_LAST: {rel}")

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

    ok = not errors and all(c["ok"] for c in checks)
    return DoctorReport(ok=ok, checks=checks, errors=errors, marketing="PARKED_LAST")
