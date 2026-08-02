"""Engage API — read/comment only on allowlisted targets."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Dict, Optional

from agent.demand_os.connectors.allowlist import (
    AllowlistError,
    require_engage_target,
)
from agent.demand_os.connectors.anti_spam import (
    AntiSpamError,
    append_engage_log,
    assert_comment_allowed,
    make_log_record,
)
from agent.demand_os.connectors.transport import (
    CommentResult,
    ReadResult,
    get_transport,
)
from agent.demand_os.publish_request import PublishRequest
from agent.demand_os.utm_lock import build_wizard_utm, validate_utm_url
from agent.demand_os.validator import evaluate_publish_request

_URL_RE = re.compile(r"https?://[^\s]+", re.IGNORECASE)


def read_target(
    target_id: str,
    *,
    mode: str = "mock",
    allowlist_path: Optional[Path] = None,
    log_path: Optional[Path] = None,
) -> ReadResult:
    target = require_engage_target(target_id, path=allowlist_path)
    transport = get_transport(mode, platform=target.platform)
    result = transport.read(
        target_id=target.id,
        platform=target.platform,
        external_id=target.external_id,
    )
    append_engage_log(
        make_log_record(
            action="read",
            target_id=target.id,
            platform=target.platform,
            kind=target.kind,
            dry_run=mode != "live",
            ok=result.ok,
            notes=result.error or f"items={len(result.items)} mode={result.mode}",
        ),
        path=log_path,
    )
    return result


def comment_on_target(
    target_id: str,
    text: str,
    *,
    mode: str = "mock",
    dry_run: bool = True,
    asset_id: str = "engage_reply",
    icp_role: str = "installateur",
    allowlist_path: Optional[Path] = None,
    log_path: Optional[Path] = None,
    skip_validator: bool = False,
) -> Dict[str, Any]:
    """
    Comment/reply on allowlisted target.
    If text contains Wizard URL → must PASS F2 Validator (content_type=reply).
    Anti-spam enforced for groups.
    """
    target = require_engage_target(target_id, path=allowlist_path)
    body = (text or "").strip()
    if not body:
        raise ValueError("comment text required")

    try:
        fp = assert_comment_allowed(
            text=body,
            target_id=target.id,
            target_kind=target.kind,
            path=log_path,
        )
    except AntiSpamError:
        append_engage_log(
            make_log_record(
                action="comment",
                target_id=target.id,
                platform=target.platform,
                kind=target.kind,
                text=body,
                dry_run=dry_run,
                ok=False,
                notes="anti_spam",
            ),
            path=log_path,
        )
        raise

    val_decision = None
    urls = _URL_RE.findall(body)
    wizard_urls = [u for u in urls if "zzpackage.flexgrafik.nl" in u]
    if wizard_urls and not skip_validator:
        utm = wizard_urls[0].rstrip(").,]")
        # If bare/invalid, try rebuild from context
        check = validate_utm_url(utm)
        if not check["ok"]:
            utm = build_wizard_utm(target.platform if target.platform != "tiktok" else "tiktok", icp_role, asset_id)
            # still validate the link present in text — must be locked form
            raise AllowlistError(
                f"comment Wizard URL fails UTM Lock: {check.get('errors')}"
            )
        req = PublishRequest(
            asset_id=asset_id,
            channel=target.platform if target.platform in ("tiktok", "facebook") else "facebook",
            icp_role=icp_role,
            caption=body,
            utm_link=utm,
            content_type="reply",
        )
        val_decision = evaluate_publish_request(
            req, log=False, emit_events=False
        )
        if not val_decision.ok:
            append_engage_log(
                make_log_record(
                    action="comment",
                    target_id=target.id,
                    platform=target.platform,
                    kind=target.kind,
                    text=body,
                    dry_run=dry_run,
                    ok=False,
                    notes=f"validator_fail:{'|'.join(val_decision.fail_rules)}",
                ),
                path=log_path,
            )
            raise AllowlistError(
                f"validator FAIL: {val_decision.fail_rules}"
            )

    transport = get_transport(mode, platform=target.platform)
    result: CommentResult = transport.comment(
        target_id=target.id,
        platform=target.platform,
        external_id=target.external_id,
        text=body,
        dry_run=dry_run,
    )
    append_engage_log(
        make_log_record(
            action="comment",
            target_id=target.id,
            platform=target.platform,
            kind=target.kind,
            text=body,
            dry_run=dry_run or result.dry_run,
            ok=result.ok,
            notes=result.error or f"cmt={result.comment_id} mode={result.mode} fp={fp}",
        ),
        path=log_path,
    )
    try:
        from agent.demand_os.audit_log import append_audit

        append_audit(
            "engage_comment",
            actor="Agent_FB" if target.platform == "facebook" else "Agent_TT",
            detail={
                "target_id": target.id,
                "ok": result.ok,
                "dry_run": dry_run or result.dry_run,
                "asset_id": asset_id,
            },
        )
    except Exception:
        pass
    a2a_record = None
    if result.ok and wizard_urls:
        from agent.demand_os.a2a_bus import emit_handoff

        a2a_record = emit_handoff(
            "engage_event",
            asset_id=asset_id,
            from_agent="Agent_FB" if target.platform == "facebook" else "Agent_TT",
            to_agent="Sales",
            payload={
                "target_id": target.id,
                "utm_link": wizard_urls[0].rstrip(").,]"),
                "dry_run": dry_run or result.dry_run,
            },
        )
    return {
        "ok": result.ok,
        "comment": result.__dict__,
        "fingerprint": fp,
        "validator": val_decision.to_dict() if val_decision else None,
        "a2a": a2a_record,
    }
