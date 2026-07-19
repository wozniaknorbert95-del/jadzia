"""Paste-ready ticket builder v1 — F4b (Ads API create PARK)."""

from __future__ import annotations

from typing import Any, Dict, List, Optional

PASTE_READY_VERSION = 1
CAMPAIGN_REF = "zzp_branding_check_v1"
BUDGET_HINT_EUR_DAY = 5
HOLD_RULE = "no_adset_edit_7d"
PLAYBOOK_REF = "docs/ops/marketing/META-PACK-LEAN.md"
TG_TEXT_MAX = 3500

EXECUTABLE_ACTIONS = frozenset(
    {
        "propose_boost",
        "block_scale",
        "propose_kill",
        "propose_pause",
        "propose_budget_cut",
    }
)


def is_paste_executable(shadow: Dict[str, Any]) -> bool:
    """Whether APPROVE in propose should auto-run ticket_only execute."""
    action = (shadow.get("proposed_action") or "").strip()
    if action == "hold":
        return False
    if action in EXECUTABLE_ACTIONS:
        return True
    return bool(shadow.get("would_execute"))


def _payload(shadow: Dict[str, Any]) -> Dict[str, Any]:
    p = shadow.get("payload") or {}
    return p if isinstance(p, dict) else {}


def _dims(shadow: Dict[str, Any]) -> Dict[str, Any]:
    dims = _payload(shadow).get("dims") or {}
    return dims if isinstance(dims, dict) else {}


def _severity(shadow: Dict[str, Any]) -> str:
    sev = (_payload(shadow).get("severity") or "ACTION").upper()
    return sev if sev in ("CRITICAL", "HIGH", "ACTION", "INFO", "MEDIUM", "LOW") else "ACTION"


def _severity_to_commander(sev: str) -> str:
    m = {
        "CRITICAL": "CRITICAL",
        "HIGH": "HIGH",
        "ACTION": "HIGH",
        "MEDIUM": "MEDIUM",
        "INFO": "LOW",
        "LOW": "LOW",
    }
    return m.get((sev or "HIGH").upper(), "HIGH")


def _truncate_tg(text: str, commander_ticket_id: Optional[int] = None) -> str:
    if len(text) <= TG_TEXT_MAX:
        return text
    marker = (
        f"\n…[full in Commander #{commander_ticket_id}]"
        if commander_ticket_id
        else "\n…[truncated — see Commander ticket]"
    )
    keep = TG_TEXT_MAX - len(marker)
    return text[: max(0, keep)] + marker


def _base(
    shadow: Dict[str, Any],
    ticket_id: str,
    *,
    fields: Dict[str, Any],
    checklist: List[str],
    create_commander_ticket: bool,
) -> Dict[str, Any]:
    action = shadow.get("proposed_action") or "unknown"
    sev = _severity(shadow)
    body = {
        "version": PASTE_READY_VERSION,
        "ticket_id": ticket_id,
        "commander_ticket_id": None,
        "action_id": shadow.get("action_id"),
        "proposed_action": action,
        "heuristic_rule_id": shadow.get("heuristic_rule_id"),
        "severity": sev,
        "commander_severity": _severity_to_commander(sev),
        "campaign_ref": CAMPAIGN_REF,
        "budget_hint_eur_day": BUDGET_HINT_EUR_DAY,
        "hold_rule": HOLD_RULE,
        "ads_api_create": "PARK",
        "playbook_ref": PLAYBOOK_REF,
        "create_commander_ticket": create_commander_ticket,
        "fields": fields,
        "checklist": checklist,
        "rationale_nl": shadow.get("llm_rationale_nl") or "",
    }
    text = _render_text(body)
    body["text"] = text
    body["text_tg"] = _truncate_tg(text)
    return body


def _render_text(body: Dict[str, Any]) -> str:
    lines = [
        f"=== MB PASTE-READY v{body['version']} ===",
        f"ticket_id: {body['ticket_id']}",
        f"action_id: {body['action_id']}",
        f"proposed_action: {body['proposed_action']}",
        f"rule: {body['heuristic_rule_id']}",
        f"severity: {body['severity']}",
        f"campaign: {body['campaign_ref']}",
        f"budget_hint: €{body['budget_hint_eur_day']}/dzień (LIVE hold)",
        f"hold_rule: {body['hold_rule']}",
        "Ads API create: PARK — wklej ręcznie w Ads Manager",
        f"playbook: {body['playbook_ref']}",
        "",
        "--- rationale ---",
        str(body.get("rationale_nl") or "(brak)"),
        "",
        "--- fields ---",
    ]
    for k, v in (body.get("fields") or {}).items():
        lines.append(f"{k}: {v}")
    lines.append("")
    lines.append("--- checklist ---")
    for i, step in enumerate(body.get("checklist") or [], 1):
        lines.append(f"{i}. {step}")
    return "\n".join(lines)


def _template_boost(shadow: Dict[str, Any], ticket_id: str) -> Dict[str, Any]:
    dims = _dims(shadow)
    fields = {
        "post_id": dims.get("post_id") or dims.get("id") or "?",
        "lift_pct": dims.get("lift_pct"),
        "quality_clean": dims.get("quality_clean", True),
        "organic_er": dims.get("er") or dims.get("organic_er"),
        "link_clicks": dims.get("link_clicks") or dims.get("clicks"),
        "utm_hint": (
            "utm_source=meta&utm_medium=paid"
            f"&utm_campaign={CAMPAIGN_REF}&utm_content=boost_organic"
        ),
    }
    checklist = [
        "Otwórz Ads Manager → kampania zzp_branding_check_v1 (HOLD €5/dzień).",
        f"Rozważ boost / wykorzystanie organic post_id={fields['post_id']} "
        f"(lift={fields.get('lift_pct')}%).",
        "NIE twórz kampanii przez Ads API — tylko UI / paste.",
        "Nie edytuj ad setu przez 7 dni (learning).",
        "UTM: " + str(fields["utm_hint"]),
        "Po leadzie: WA <15 min (SPEED-TO-LEAD).",
    ]
    return _base(
        shadow,
        ticket_id,
        fields=fields,
        checklist=checklist,
        create_commander_ticket=True,
    )


def _template_hold(shadow: Dict[str, Any], ticket_id: str) -> Dict[str, Any]:
    facts = _payload(shadow).get("facts_summary") or {}
    fields = {
        "mode": "observability_ack",
        "margin_avg_pct": facts.get("margin_avg_pct"),
        "attribution_coverage_pct": facts.get("attribution_coverage_pct"),
        "red_flags": facts.get("red_flags"),
    }
    checklist = [
        "ACK only — brak wklejania do Ads Manager.",
        "Kontynuuj shadow/propose observation.",
        "Nie scale bez sygnału.",
    ]
    return _base(
        shadow,
        ticket_id,
        fields=fields,
        checklist=checklist,
        create_commander_ticket=False,
    )


def _template_block(shadow: Dict[str, Any], ticket_id: str) -> Dict[str, Any]:
    dims = _dims(shadow)
    facts = _payload(shadow).get("facts_summary") or {}
    fields = {
        "stop": "NO_SCALE",
        "dims": {k: dims.get(k) for k in list(dims)[:12]},
        "margin_avg_pct": facts.get("margin_avg_pct"),
        "attribution_coverage_pct": facts.get("attribution_coverage_pct"),
        "red_flags": facts.get("red_flags"),
    }
    checklist = [
        "STOP scale / nie podnoś budżetu.",
        "Sprawdź Data Health (margin / attribution / pixel).",
        "Ads API create: PARK.",
        "Po naprawie faktów — nowy cykl MB, nie ręczny force.",
    ]
    return _base(
        shadow,
        ticket_id,
        fields=fields,
        checklist=checklist,
        create_commander_ticket=True,
    )


def _template_generic(shadow: Dict[str, Any], ticket_id: str) -> Dict[str, Any]:
    dims = _dims(shadow)
    fields = {
        "raw_action": shadow.get("proposed_action"),
        "dims_keys": list(dims.keys())[:20],
        "dims": {k: dims.get(k) for k in list(dims)[:10]},
    }
    checklist = [
        "Przejrzyj rationale i rule_id.",
        "Jeśli dotyczy Ads — tylko UI paste; Ads API create PARK.",
        f"Kampania ref: {CAMPAIGN_REF} · budżet hint €{BUDGET_HINT_EUR_DAY}/d.",
        "Playbook: " + PLAYBOOK_REF,
    ]
    return _base(
        shadow,
        ticket_id,
        fields=fields,
        checklist=checklist,
        create_commander_ticket=True,
    )


def build_paste_ready(shadow: Dict[str, Any], ticket_id: str) -> Dict[str, Any]:
    """Pure builder — no I/O. Returns paste_ready v1 dict."""
    action = (shadow.get("proposed_action") or "").strip()
    if action == "propose_boost":
        return _template_boost(shadow, ticket_id)
    if action == "hold":
        return _template_hold(shadow, ticket_id)
    if action in ("block_scale", "propose_kill", "propose_pause", "propose_budget_cut"):
        return _template_block(shadow, ticket_id)
    # attribution / margin style holds often use hold — already covered
    rule = (shadow.get("heuristic_rule_id") or "").upper()
    if "ATTRIBUTION" in rule or "MARGIN" in rule or "BLOCK" in rule:
        return _template_block(shadow, ticket_id)
    return _template_generic(shadow, ticket_id)


def attach_commander_id(paste: Dict[str, Any], commander_ticket_id: Optional[int]) -> Dict[str, Any]:
    """Update paste with commander id and refresh text_tg truncation marker."""
    out = dict(paste)
    out["commander_ticket_id"] = commander_ticket_id
    text = out.get("text") or ""
    out["text_tg"] = _truncate_tg(text, commander_ticket_id)
    return out
