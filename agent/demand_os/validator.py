"""Sniper Validator engine — OS C.5 rules as deterministic code."""

from __future__ import annotations

import csv
import hashlib
import re
import time
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

from agent.demand_os.growth_events import append_growth_event
from agent.demand_os.publish_request import PublishRequest
from agent.demand_os.utm_lock import validate_utm_url

# Ads freeze SoT: docs/ops/demand-os/set-now/ADS-FREEZE.md
ADS_FREEZE_UNTIL = date(2026, 8, 6)

# C.5 checklist → stable rule IDs (never renumber casually)
RULE_R1_MULTI_CTA_URL = "R1_multi_cta_url"
RULE_R2_UTM_MISSING = "R2_utm_missing_or_invalid"
RULE_R3_ICP_ROLE = "R3_icp_role_missing_or_mismatch"
RULE_R4_MULTI_CTA_WORDS = "R4_multi_cta_words"
RULE_R5_ADS_FREEZE = "R5_ads_in_freeze"
RULE_R6_HQ_HERO = "R6_hq_hero"
RULE_R7_OFFERTE_ONLY = "R7_offerte_only"
RULE_R8_GAME_DUAL_CTA = "R8_game_dual_cta"
RULE_R9_DECOY_MENU = "R9_decoy_menu_in_post"

ALL_RULES = (
    RULE_R1_MULTI_CTA_URL,
    RULE_R2_UTM_MISSING,
    RULE_R3_ICP_ROLE,
    RULE_R4_MULTI_CTA_WORDS,
    RULE_R5_ADS_FREEZE,
    RULE_R6_HQ_HERO,
    RULE_R7_OFFERTE_ONLY,
    RULE_R8_GAME_DUAL_CTA,
    RULE_R9_DECOY_MENU,
)

# Engagement bait / multi-ask (word boundaries; NL + EN)
_MULTI_CTA_PATTERNS = [
    r"\blike\b",
    r"\bcomment\b",
    r"\bsave\b",
    r"\bshare\b",
    r"\bfollow\b",
    r"\bsubscribe\b",
    r"\bnewsletter\b",
    r"\bbuy\b",
    r"\bshop\s+now\b",
    r"\breageer\b",
    r"\bbewaar\b",
    r"\bvolg\b",
    r"\bnieuwsbrief\b",
    r"\bkoop\b",
    r"\bbestel\s+nu\b",
    r"\blink\s+in\s+bio\b",
]
_MULTI_CTA_RE = re.compile("|".join(_MULTI_CTA_PATTERNS), re.IGNORECASE)

_HQ_HERO_RE = re.compile(
    r"\b(vhq|agent\s*os|mission\s*control|dashboard|hq\s*screenshot)\b",
    re.IGNORECASE,
)
# B.9 — post must not present package menu (Wizard holds packs)
_DECOY_MENU_RE = re.compile(
    r"(\bpakket\s*[abc]\b|\bkies\s+(je|uw)\s+pakket\b|€\s*\d{2,}.+€\s*\d{2,})",
    re.IGNORECASE | re.DOTALL,
)
_GAME_HOST = "app.flexgrafik.nl"
_WIZARD_HOST = "zzpackage.flexgrafik.nl"

_REPO = Path(__file__).resolve().parents[2]
_DEFAULT_LOG = _REPO / "docs/ops/demand-os/set-now/VALIDATOR-LOG.csv"


def default_validator_log_path() -> Path:
    """Writable log path — prod set-now is read-only, fall back to data/."""
    from agent.demand_os.state_paths import resolve_writable_path

    return resolve_writable_path(
        _DEFAULT_LOG.name, env_var="DEMAND_OS_VALIDATOR_LOG"
    )


@dataclass
class ValidatorDecision:
    request_id: str
    asset_id: str
    channel: str
    icp_role: str
    decision: str  # PASS | FAIL
    fail_rules: List[str] = field(default_factory=list)
    utm_ok: bool = False
    pass_token: Optional[str] = None
    decision_ms: float = 0.0
    decided_at: str = ""
    notes: str = ""
    details: Dict[str, Any] = field(default_factory=dict)

    @property
    def ok(self) -> bool:
        return self.decision == "PASS"

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _as_of(value: Optional[date]) -> date:
    return value or datetime.now(timezone.utc).date()


def _mint_pass_token(req: PublishRequest, decided_at: str) -> str:
    raw = f"{req.request_id}|{req.asset_id}|{req.channel}|{req.utm_link}|{decided_at}|PASS"
    digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:20]
    return f"val_{digest}"


def _unique_urls(*parts: str) -> set[str]:
    found: set[str] = set()
    for part in parts:
        for u in re.findall(r"https?://[^\s]+", part or "", flags=re.IGNORECASE):
            found.add(u.rstrip(").,]").lower())
    return found


def evaluate_publish_request(
    req: PublishRequest,
    *,
    as_of: Optional[date] = None,
    log: bool = True,
    log_path: Optional[Path] = None,
    emit_events: bool = True,
) -> ValidatorDecision:
    """
    Run C.5 rules. Binary PASS/FAIL.
    On PASS: mint pass_token. Optionally append VALIDATOR-LOG + growth_events.
    """
    t0 = time.perf_counter()
    shape_errors = req.validate_shape()
    fail: List[str] = []
    details: Dict[str, Any] = {"shape_errors": shape_errors}
    utm_ok = False
    day = _as_of(as_of)

    if shape_errors:
        # Shape failure maps to closest rules for operator clarity
        fail.append(RULE_R3_ICP_ROLE if any("icp_role" in e for e in shape_errors) else RULE_R2_UTM_MISSING)
        details["hard_shape"] = True

    caption = req.caption or ""
    blob = f"{caption}\n{req.utm_link}".strip()

    # R1 — more than one distinct URL CTA (same link in caption+utm_link = OK)
    if len(_unique_urls(caption, req.utm_link or "")) > 1:
        fail.append(RULE_R1_MULTI_CTA_URL)

    # R8 — game post must not carry Wizard CTA
    if req.content_type == "game_post":
        if _WIZARD_HOST in blob.lower() or "utm_source=" in blob.lower():
            fail.append(RULE_R8_GAME_DUAL_CTA)
        if _GAME_HOST not in blob.lower() and "http" in blob.lower():
            # has URL but not game host
            fail.append(RULE_R8_GAME_DUAL_CTA)
    else:
        # R2 — UTM Lock (F1)
        utm_result = validate_utm_url(req.utm_link)
        utm_ok = bool(utm_result.get("ok"))
        details["utm"] = utm_result
        if not utm_ok:
            fail.append(RULE_R2_UTM_MISSING)
        else:
            parts = utm_result.get("parts") or {}
            # R3 — icp_role tag consistency (campaign + request)
            if parts.get("role") != req.icp_role:
                fail.append(RULE_R3_ICP_ROLE)
            if parts.get("channel") and parts.get("channel") != req.channel:
                details["channel_mismatch"] = {
                    "request": req.channel,
                    "utm": parts.get("channel"),
                }
                fail.append(RULE_R3_ICP_ROLE)
            if parts.get("asset_id") and parts.get("asset_id") != req.asset_id:
                details["asset_mismatch"] = True
                fail.append(RULE_R3_ICP_ROLE)

    # R3 — role must also appear as hashtag/tag signal in caption for posts
    if req.content_type == "organic_post":
        role_tag = f"#{req.icp_role}".lower()
        role_plain = req.icp_role.lower()
        cap_l = caption.lower()
        if role_tag not in cap_l and f"icp_role={role_plain}" not in cap_l:
            # allow role word presence for NL captions (#installateur)
            if f"#{role_plain}" not in cap_l and role_plain not in cap_l:
                fail.append(RULE_R3_ICP_ROLE)

    # R4 — multi-CTA bait words
    if _MULTI_CTA_RE.search(caption):
        fail.append(RULE_R4_MULTI_CTA_WORDS)

    # R5 — ads / paid boost during freeze
    if req.ads_boost or (req.channel == "meta" and "paid" in (req.utm_link or "").lower()):
        if day < ADS_FREEZE_UNTIL:
            fail.append(RULE_R5_ADS_FREEZE)
    if "utm_medium=paid" in (req.utm_link or "").lower() and day < ADS_FREEZE_UNTIL:
        fail.append(RULE_R5_ADS_FREEZE)

    # R6 — HQ / dashboard as hero
    if req.hero_is_hq or _HQ_HERO_RE.search(caption):
        fail.append(RULE_R6_HQ_HERO)

    # R7 — offerte as only next step
    if req.offerte_only:
        fail.append(RULE_R7_OFFERTE_ONLY)
    elif re.search(r"\bofferte\b", caption, re.IGNORECASE) and "wizard" not in caption.lower():
        fail.append(RULE_R7_OFFERTE_ONLY)

    # R9 — B.9 decoy: package menu in social post (Wizard holds packs)
    if req.content_type == "organic_post" and _DECOY_MENU_RE.search(caption):
        fail.append(RULE_R9_DECOY_MENU)

    # Dedupe fail rules preserving order
    seen = set()
    ordered: List[str] = []
    for r in fail:
        if r not in seen:
            seen.add(r)
            ordered.append(r)

    decided_at = _utc_now()
    decision = "PASS" if not ordered else "FAIL"
    token = _mint_pass_token(req, decided_at) if decision == "PASS" else None
    ms = (time.perf_counter() - t0) * 1000.0

    result = ValidatorDecision(
        request_id=req.request_id,
        asset_id=req.asset_id,
        channel=req.channel,
        icp_role=req.icp_role,
        decision=decision,
        fail_rules=ordered,
        utm_ok=utm_ok,
        pass_token=token,
        decision_ms=round(ms, 3),
        decided_at=decided_at,
        notes="",
        details=details,
    )

    if log:
        append_validator_log(result, path=log_path or default_validator_log_path(), publish_intended="N")
    if emit_events:
        append_growth_event(
            "cta_validated" if result.ok else "cta_rejected",
            asset_id=req.asset_id,
            channel=req.channel,
            utm_link=req.utm_link,
            ok=result.ok,
            errors=result.fail_rules,
            notes=f"validator {result.decision} token={result.pass_token or '-'}",
        )
        try:
            from agent.demand_os.audit_log import append_audit

            append_audit(
                "validator_pass" if result.ok else "validator_fail",
                actor="Sniper_Validator",
                detail={
                    "asset_id": req.asset_id,
                    "decision": result.decision,
                    "fail_rules": result.fail_rules,
                },
            )
        except Exception:
            pass
    if result.ok and emit_events:
        try:
            from agent.demand_os.a2a_bus import ack_handoff, emit_handoff

            emitted = emit_handoff(
                "publish_request",
                asset_id=req.asset_id,
                from_agent="Content_Factory",
                to_agent="Sniper_Validator",
                payload={
                    "request_id": req.request_id,
                    "pass_token": result.pass_token,
                    "channel": req.channel,
                },
            )
            ack_handoff(emitted["id"])
        except Exception:
            pass
    return result


def append_validator_log(
    decision: ValidatorDecision,
    *,
    path: Path,
    publish_intended: str = "N",
) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    write_header = not path.is_file()
    fieldnames = [
        "date",
        "asset_id",
        "channel",
        "icp_role",
        "decision",
        "fail_rules",
        "utm_ok",
        "publish_intended",
        "notes",
    ]
    day = decision.decided_at[:10] if decision.decided_at else date.today().isoformat()
    row = {
        "date": day,
        "asset_id": decision.asset_id,
        "channel": decision.channel,
        "icp_role": decision.icp_role,
        "decision": decision.decision,
        "fail_rules": "|".join(decision.fail_rules),
        "utm_ok": "Y" if decision.utm_ok else "N",
        "publish_intended": publish_intended,
        "notes": (
            f"req={decision.request_id} ms={decision.decision_ms}"
            f" token={decision.pass_token or '-'}"
        ),
    }
    with path.open("a", encoding="utf-8", newline="") as fh:
        writer = csv.DictWriter(fh, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()
        writer.writerow(row)


def verify_pass_token(req: PublishRequest, token: str, decided_at: str) -> bool:
    """Recompute token; used by gate before any publish path."""
    if not token or not token.startswith("val_"):
        return False
    return token == _mint_pass_token(req, decided_at)


def rules_catalog() -> Sequence[str]:
    return ALL_RULES
