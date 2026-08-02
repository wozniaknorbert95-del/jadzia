"""Blog ICP pipeline — OS C.4 / F4 (1 role per article · Wizard UTM blog · Val C.5)."""

from __future__ import annotations

import json
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.content_calendar import (
    CalendarSlot,
    add_slot,
    load_calendar,
    save_calendar,
    set_slot_status,
)
from agent.demand_os.publish_request import PublishRequest
from agent.demand_os.utm_lock import build_wizard_utm
from agent.demand_os.validator import ValidatorDecision, evaluate_publish_request

_REPO = Path(__file__).resolve().parents[2]
DEFAULT_DRAFTS_DIR = _REPO / "docs/ops/demand-os/set-now/BLOG-DRAFTS"

# ICP roles allowed for Demand OS content (extend deliberately)
ALLOWED_ICP_ROLES = frozenset(
    {
        "installateur",
        "hovenier",
        "elektricien",
        "schilder",
        "zzp_bouw",
    }
)

# Explicit ban — no generic "AI blog" path
BANNED_ROLES = frozenset({"", "general", "all", "everyone", "business", "tips"})

# Week-1 SoT angle (OS C.4) — installateur
_WEEK1_INSTALLATEUR = {
    "slug": "witte-bus-50m-herkenbaar",
    "title": "Witte bus op 50 meter: anoniem of herkenbaar?",
    "angle": "bus_50m_herkenbaar",
    "body": """## Voor de installateur die wil dat klanten je herkennen

Rijd je met een witte bus door de wijk, dan ben je op 50 meter gewoon *nog een bus*.
Geen naam. Geen vak. Geen reden om te bellen.

Voor **installateur** / ZZP in de bouw en techniek is herkenbaarheid geen vanity —
het is hoe opdrachtgevers je onthouden tussen tien andere bussen op de stoep.

### Wat wél werkt (simpel)

1. **Grote naam** op de zijkant — leesbaar vanaf de weg.
2. **Vakwoord** (installatie / elektra / loodgieter) — niet alleen een logo.
3. **Telefoon of Wizard-link** als enige volgende stap — geen rommel van vijf CTA's.

### Wat je níet doet

- Geen HQ-screenshot als hero.
- Geen engagement-bait / multi-ask.
- Geen tweede link naast de Wizard.

### Volgende stap

Configureer jouw buspakket in de Wizard — één pad, geen vrijblijvende offerte-praat.
""",
}

_ROLE_ANGLES: Dict[str, Dict[str, str]] = {
    "installateur": _WEEK1_INSTALLATEUR,
    "hovenier": {
        "slug": "hovenier-bus-herkenbaar-wijk",
        "title": "Hovenier: waarom jouw bus in de wijk moet opvallen",
        "angle": "hovenier_bus_wijk",
        "body": """## Voor de hovenier die lokaal wil groeien

Particulieren en VvE's zien tientallen busjes. Jouw **hovenier**-bus moet in één oogopslag
zeggen: tuinonderhoud / aanleg — bel of start in de Wizard.

Eén CTA. Geen multi-link bio-chaos.
""",
    },
    "elektricien": {
        "slug": "elektricien-bus-zichtbaar",
        "title": "Elektricien: zichtbaarheid op de bus = meer belletjes",
        "angle": "elektricien_bus",
        "body": """## Voor de elektricien / ZZP techniek

Een anonieme bus kost je leads. Zet vak + naam groot; stuur alles naar één Wizard-pad.
""",
    },
    "schilder": {
        "slug": "schilder-bus-merk",
        "title": "Schilder: jouw bus als rijdend visitekaartje",
        "angle": "schilder_bus",
        "body": """## Voor de schilder die wil dat buren je onthouden

Rol + kleuren + één CTA naar de Wizard. Geen tweede link.
""",
    },
    "zzp_bouw": {
        "slug": "zzp-bouw-bus-herkenbaar",
        "title": "ZZP bouw: herkenbare bus, één route naar klanten",
        "angle": "zzp_bouw_bus",
        "body": """## Voor ZZP'ers in de bouw

Opdrachtgevers scrollen voorbij anonieme bussen. Merk + vak + Wizard. Klaar.
""",
    },
}


class BlogPipelineError(ValueError):
    """Raised when blog ICP pipeline input violates C.4 / F4 rules."""


@dataclass
class BlogArticle:
    asset_id: str
    icp_role: str
    title: str
    slug: str
    angle: str
    body_md: str
    tags: List[str] = field(default_factory=list)
    utm_link: str = ""
    channel: str = "blog"
    status: str = "draft"  # draft | validated | rejected
    pass_token: Optional[str] = None
    request_id: Optional[str] = None
    created_at: str = ""
    fail_rules: List[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def caption_for_validator(self) -> str:
        """Flat caption blob used by Sniper Validator (C.5 tag + single CTA)."""
        tag_line = f"icp_role={self.icp_role} #{self.icp_role}"
        tags = " ".join(f"#{t}" for t in self.tags if t and t != self.icp_role)
        return (
            f"{self.title}\n\n"
            f"{self.body_md.strip()}\n\n"
            f"{tag_line}\n"
            f"{tags}\n"
            f"{self.utm_link}"
        ).strip()


def _utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def _slugify(text: str) -> str:
    s = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return s[:64] or "blog-draft"


def normalize_icp_role(role: str) -> str:
    rl = (role or "").strip().lower().replace(" ", "_").replace("-", "_")
    if rl in BANNED_ROLES or not rl:
        raise BlogPipelineError(
            "icp_role required — generic/empty roles banned (no general AI blogs)"
        )
    if rl not in ALLOWED_ICP_ROLES:
        raise BlogPipelineError(
            f"icp_role not in allowlist: {rl!r} (allowed: {sorted(ALLOWED_ICP_ROLES)})"
        )
    return rl


def generate_article(
    icp_role: str,
    *,
    asset_id: Optional[str] = None,
    angle: Optional[str] = None,
) -> BlogArticle:
    """
    Generate one ICP-scoped blog draft.
    Hard-fails without a concrete role (F4 / C.4).
    """
    role = normalize_icp_role(icp_role)
    tmpl = _ROLE_ANGLES[role]
    if angle and angle.strip() and angle.strip().lower() not in (
        tmpl["angle"],
        "default",
        role,
    ):
        # Custom angle label allowed only as suffix metadata — body stays role-specific
        angle_key = _slugify(angle)
    else:
        angle_key = tmpl["angle"]

    aid = (asset_id or "").strip() or f"blog_{role}_{angle_key}"
    if any(c.isspace() for c in aid):
        raise BlogPipelineError(f"invalid asset_id: {aid!r}")

    utm = build_wizard_utm("blog", role, aid)
    tags = [role, "zzp", "nederland", "wizard"]
    return BlogArticle(
        asset_id=aid,
        icp_role=role,
        title=tmpl["title"],
        slug=tmpl["slug"],
        angle=angle_key,
        body_md=tmpl["body"].strip() + "\n",
        tags=tags,
        utm_link=utm,
        channel="blog",
        status="draft",
        created_at=_utc_now(),
        notes="F4 blog_pipeline deterministic ICP draft",
    )


def article_to_publish_request(article: BlogArticle) -> PublishRequest:
    return PublishRequest(
        asset_id=article.asset_id,
        channel="blog",
        icp_role=article.icp_role,
        caption=article.caption_for_validator(),
        utm_link=article.utm_link,
        content_type="organic_post",
        hero_is_hq=False,
        ads_boost=False,
        offerte_only=False,
        meta={"slug": article.slug, "angle": article.angle, "tags": list(article.tags)},
    )


def validate_article(
    article: BlogArticle,
    *,
    log: bool = True,
    emit_events: bool = False,
    log_path: Optional[Path] = None,
) -> tuple[BlogArticle, ValidatorDecision]:
    req = article_to_publish_request(article)
    decision = evaluate_publish_request(
        req,
        log=log,
        emit_events=emit_events,
        log_path=log_path,
    )
    out = BlogArticle(**article.to_dict())
    out.request_id = decision.request_id
    if decision.ok:
        out.status = "validated"
        out.pass_token = decision.pass_token
        out.fail_rules = []
        out.notes = f"Val PASS {decision.decided_at}"
    else:
        out.status = "rejected"
        out.pass_token = None
        out.fail_rules = list(decision.fail_rules)
        out.notes = f"Val FAIL {decision.fail_rules}"
    return out, decision


def persist_article(article: BlogArticle, drafts_dir: Optional[Path] = None) -> Path:
    root = drafts_dir or DEFAULT_DRAFTS_DIR
    root.mkdir(parents=True, exist_ok=True)
    json_path = root / f"{article.asset_id}.json"
    md_path = root / f"{article.asset_id}.md"
    json_path.write_text(
        json.dumps(article.to_dict(), ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    md = (
        f"---\n"
        f"asset_id: {article.asset_id}\n"
        f"icp_role: {article.icp_role}\n"
        f"channel: blog\n"
        f"status: {article.status}\n"
        f"utm: {article.utm_link}\n"
        f"pass_token: {article.pass_token or ''}\n"
        f"---\n\n"
        f"# {article.title}\n\n"
        f"{article.body_md.strip()}\n\n"
        f"---\n"
        f"CTA: {article.utm_link}\n"
        f"Tags: icp_role={article.icp_role} "
        + " ".join(f"#{t}" for t in article.tags)
        + "\n"
    )
    md_path.write_text(md, encoding="utf-8")
    return json_path


def bind_calendar(article: BlogArticle, *, slot_date: Optional[str] = None) -> None:
    """Bind validated article into content_calendar (status validated|draft)."""
    if article.status != "validated" or not article.pass_token:
        raise BlogPipelineError("calendar bind requires validated article + pass_token")
    cal = load_calendar()
    day = slot_date or datetime.now(timezone.utc).date().isoformat()
    try:
        cal = set_slot_status(
            cal,
            asset_id=article.asset_id,
            status="validated",
            request_id=article.request_id or "",
            pass_token=article.pass_token,
            notes=article.notes,
        )
    except KeyError:
        cal = add_slot(
            cal,
            CalendarSlot(
                date=day,
                channel="blog",
                asset_id=article.asset_id,
                status="validated",
                request_id=article.request_id or "",
                pass_token=article.pass_token,
                notes=f"icp_role={article.icp_role} | {article.utm_link} | {article.notes}",
            ),
        )
    save_calendar(cal)


def run_pipeline(
    icp_role: str,
    *,
    asset_id: Optional[str] = None,
    angle: Optional[str] = None,
    persist: bool = True,
    calendar: bool = True,
    drafts_dir: Optional[Path] = None,
    log: bool = True,
    emit_events: bool = False,
) -> Dict[str, Any]:
    """Generate → validate C.5 → persist draft → optional calendar bind."""
    article = generate_article(icp_role, asset_id=asset_id, angle=angle)
    article, decision = validate_article(
        article, log=log, emit_events=emit_events
    )
    paths: Dict[str, str] = {}
    if persist:
        p = persist_article(article, drafts_dir=drafts_dir)
        paths["json"] = str(p)
        paths["md"] = str(p.with_suffix(".md"))
    cal_bound = False
    if calendar and article.status == "validated":
        bind_calendar(article)
        cal_bound = True
    return {
        "article": article.to_dict(),
        "decision": decision.to_dict(),
        "paths": paths,
        "calendar_bound": cal_bound,
    }


def list_drafts(drafts_dir: Optional[Path] = None) -> List[Dict[str, Any]]:
    root = drafts_dir or DEFAULT_DRAFTS_DIR
    if not root.exists():
        return []
    out: List[Dict[str, Any]] = []
    for path in sorted(root.glob("*.json")):
        try:
            out.append(json.loads(path.read_text(encoding="utf-8")))
        except Exception as exc:  # noqa: BLE001 — list best-effort
            out.append({"asset_id": path.stem, "error": str(exc)})
    return out
