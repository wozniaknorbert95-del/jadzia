"""UTM Lock — single CTA Wizard URL template (OS C.1 #3)."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

WIZARD_HOST = "zzpackage.flexgrafik.nl"
WIZARD_PATH = "/wizard/"
DEFAULT_MEDIUM = "organic"

ALLOWED_CHANNELS = frozenset(
    {
        "tiktok",
        "facebook",
        "blog",
        "design_agent",
        "whatsapp",
        "widget",
        "meta",
    }
)


class UtmLockError(ValueError):
    """Raised when a growth CTA fails UTM Lock rules."""


@dataclass(frozen=True)
class UtmParts:
    channel: str
    role: str
    asset_id: str
    medium: str = DEFAULT_MEDIUM

    @property
    def campaign(self) -> str:
        return f"icp_{self.role}"


def build_wizard_utm(
    channel: str,
    role: str,
    asset_id: str,
    *,
    medium: str = DEFAULT_MEDIUM,
    extra: Optional[Dict[str, str]] = None,
) -> str:
    """Build the canonical Wizard CTA URL (exactly one CTA, full UTM).

    Optional ``extra`` query keys (e.g. voertuig/highlight for Design Agent)
    are appended after Lock params — never replace UTM.
    """
    ch = (channel or "").strip().lower()
    rl = (role or "").strip().lower()
    aid = (asset_id or "").strip()
    med = (medium or DEFAULT_MEDIUM).strip().lower() or DEFAULT_MEDIUM

    if not ch:
        raise UtmLockError("channel required")
    if ch not in ALLOWED_CHANNELS:
        raise UtmLockError(f"channel not allowed: {ch}")
    if not rl or not rl.replace("_", "").isalnum():
        raise UtmLockError(f"invalid icp role: {rl!r}")
    if not aid or any(c.isspace() for c in aid):
        raise UtmLockError(f"invalid asset_id: {aid!r}")
    if med != DEFAULT_MEDIUM and med != "paid":
        raise UtmLockError(f"medium must be organic|paid, got {med!r}")

    params: Dict[str, str] = {
        "utm_source": ch,
        "utm_medium": med,
        "utm_campaign": f"icp_{rl}",
        "utm_content": aid,
    }
    for key, val in (extra or {}).items():
        k = (key or "").strip()
        v = (val or "").strip()
        if not k or k.startswith("utm_"):
            continue
        if v:
            params[k] = v
    return f"https://{WIZARD_HOST}{WIZARD_PATH}?{urlencode(params)}"


def validate_utm_url(url: str) -> Dict[str, Any]:
    """
    Validate a growth CTA against C.1 #3.
    Returns dict: ok, errors[], parts{...}.
    Never raises for bad input — returns ok=False.
    """
    errors: list[str] = []
    raw = (url or "").strip()
    if not raw:
        return {"ok": False, "errors": ["empty url"], "parts": None}

    # Multi-CTA heuristic: second http(s) in same string
    lowered = raw.lower()
    if lowered.count("http://") + lowered.count("https://") > 1:
        errors.append("multi_cta: more than one URL")

    try:
        parsed = urlparse(raw.split()[0] if " " in raw else raw)
    except Exception:
        return {"ok": False, "errors": ["unparseable url"], "parts": None}

    if parsed.scheme != "https":
        errors.append("scheme must be https")
    host = (parsed.netloc or "").lower()
    if host != WIZARD_HOST:
        errors.append(f"host must be {WIZARD_HOST}")
    path = parsed.path or ""
    if path.rstrip("/") != WIZARD_PATH.rstrip("/"):
        errors.append(f"path must be {WIZARD_PATH}")

    qs = parse_qs(parsed.query, keep_blank_values=True)
    def _one(key: str) -> Optional[str]:
        vals = qs.get(key) or []
        if len(vals) != 1:
            return None
        return vals[0]

    source = _one("utm_source")
    medium = _one("utm_medium")
    campaign = _one("utm_campaign")
    content = _one("utm_content")

    if not source:
        errors.append("missing utm_source")
    elif source.lower() not in ALLOWED_CHANNELS:
        errors.append(f"utm_source not allowed: {source}")

    if not medium:
        errors.append("missing utm_medium")
    elif medium.lower() not in ("organic", "paid"):
        errors.append(f"utm_medium invalid: {medium}")

    role = None
    if not campaign:
        errors.append("missing utm_campaign")
    elif not campaign.lower().startswith("icp_"):
        errors.append("utm_campaign must start with icp_")
    else:
        role = campaign[4:]
        if not role:
            errors.append("utm_campaign missing role after icp_")

    if not content:
        errors.append("missing utm_content")
    elif any(c.isspace() for c in content):
        errors.append("utm_content must not contain whitespace")

    # Bare / vanity path without query already covered; also reject HQ vanity
    if "flexgrafik.nl" in host and host != WIZARD_HOST:
        errors.append("vanity_hq_forbidden")

    ok = len(errors) == 0
    parts = None
    if ok and source and medium and role and content:
        parts = {
            "channel": source.lower(),
            "medium": medium.lower(),
            "role": role.lower(),
            "asset_id": content,
            "campaign": f"icp_{role.lower()}",
        }
    return {"ok": ok, "errors": errors, "parts": parts}


def rewrite_to_locked(
    channel: str,
    role: str,
    asset_id: str,
    *,
    medium: str = DEFAULT_MEDIUM,
) -> str:
    """Alias — always rebuild; never trust caller-assembled query strings."""
    return build_wizard_utm(channel, role, asset_id, medium=medium)


def canonical_form(url: str) -> Optional[str]:
    """If valid, return rebuilt canonical URL; else None."""
    result = validate_utm_url(url)
    if not result["ok"] or not result["parts"]:
        return None
    p = result["parts"]
    return build_wizard_utm(
        p["channel"], p["role"], p["asset_id"], medium=p["medium"]
    )


def urlunparse_safe(parts: UtmParts) -> str:
    query = urlencode(
        {
            "utm_source": parts.channel,
            "utm_medium": parts.medium,
            "utm_campaign": parts.campaign,
            "utm_content": parts.asset_id,
        }
    )
    return urlunparse(("https", WIZARD_HOST, WIZARD_PATH, "", query, ""))
