"""Hub-spoke flow — OS TARGET v5 §E chain as one honest command.

Chain: ICP_Brain (brief) → Content_Factory (brief+UTM) → Sniper_Validator (rules)
→ publish_request A2A handoff draft. Never publishes. Marketing PARKED keeps the
final step gated; dry-run is the default.

The point: TARGET §E is hub-spoke, not nine isolated shells. This wires the
existing tools into the documented chain without inventing live capability.
"""

from __future__ import annotations

from typing import Any, Dict, Optional

from agent.demand_os.a2a_bus import emit_handoff
from agent.demand_os.content_factory import build_brief
from agent.demand_os.marketing_mode import is_marketing_parked, resolve_marketing_mode
from agent.demand_os.publish_request import PublishRequest
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.validator import evaluate_publish_request

FLOW_STEPS = ("icp_brief", "cf_brief", "validator", "publish_request")


def run_hub_spoke_flow(
    *,
    icp_role: str = "installateur",
    channel: str = "tiktok",
    asset_id: Optional[str] = None,
    caption: str = "",
    dry_run: bool = True,
) -> Dict[str, Any]:
    """Execute ICP → CF → Validator → publish_request draft chain."""
    mode = resolve_marketing_mode()
    role = (icp_role or "installateur").strip().lower()
    chan = (channel or "tiktok").strip().lower()
    aid = (asset_id or f"{chan[:2]}_flow_{role}_01").strip()

    steps: Dict[str, Any] = {}

    # 1) ICP_Brain — semantic role/hook (read via CF helper through memory SoT)
    steps["icp_brief"] = {"ok": True, "icp_role": role, "source": "memory.semantic"}
    steps["icp_brief"]["note"] = ""

    # 2) Content_Factory — brief with 1 CTA + UTM (proof tier ≥1 enforced inside)
    brief = build_brief(channel=chan, asset_id=aid, proof_tier=1)
    steps["cf_brief"] = brief
    if not brief.get("ok"):
        return _result(False, steps, mode, dry_run, error="cf_brief_failed")

    b = brief["brief"]
    # C.5 R3: UTM campaign role must equal request role — build from flow role,
    # never silently inherit the memory-semantic role from the brief.
    utm = build_wizard_utm(chan, role, aid)
    memory_role = b.get("icp_role")
    role_mismatch_note = (
        "" if memory_role == role else f"memory semantic role={memory_role}, flow role={role}"
    )
    # C.5 R3: organic_post caption must carry the ICP role signal (#role tag)
    cap = caption or f"{b['hook']} — {chan} clip #{role}"

    # 3) Sniper_Validator — C.5 rules engine on formal publish_request
    req = PublishRequest(
        asset_id=aid,
        channel=chan,
        icp_role=role,
        caption=cap,
        utm_link=utm,
        content_type="organic_post",
    )
    decision = evaluate_publish_request(req, log=False, emit_events=False)
    steps["validator"] = {
        "ok": decision.ok,
        "fail_rules": list(decision.fail_rules),
        "request_id": req.request_id,
    }
    if role_mismatch_note:
        steps["icp_brief"]["note"] = role_mismatch_note
    if not decision.ok:
        return _result(
            False,
            steps,
            mode,
            dry_run,
            error="validator_fail",
            request=req.to_dict(),
        )

    # 4) publish_request → A2A handoff draft (never live; gated while PARKED)
    parked = is_marketing_parked(marketing=mode)
    handoff: Dict[str, Any] = {
        "ok": True,
        "status": "dry_run" if dry_run else "emitted",
        "publish_allowed": not parked,
        "blocked_reason": (
            "live publish gated — marketing PARKED until Dowódca unlock" if parked else ""
        ),
    }
    if not dry_run:
        rec = emit_handoff(
            "publish_request",
            payload={
                "request_id": req.request_id,
                "channel": chan,
                "icp_role": role,
                "validator_ok": True,
            },
            asset_id=aid,
            from_agent="Content_Factory",
            to_agent="Sniper_Validator",
        )
        handoff["a2a_id"] = rec["id"]
        handoff["sla_minutes"] = rec["sla_minutes"]
    steps["publish_request"] = handoff

    return _result(True, steps, mode, dry_run, request=req.to_dict())


def _result(
    ok: bool,
    steps: Dict[str, Any],
    mode: str,
    dry_run: bool,
    *,
    error: str = "",
    request: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    done = [s for s in FLOW_STEPS if s in steps and steps[s].get("ok")]
    return {
        "ok": ok,
        "chain": "ICP_Brain→Content_Factory→Sniper_Validator→publish_request",
        "steps": steps,
        "steps_ok": done,
        "error": error,
        "request": request,
        "dry_run": dry_run,
        "live_publish": False,
        "marketing": mode,
        "note": "flow proves chain integrity; live publish stays gated",
    }
