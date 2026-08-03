"""Demand Desk v2.1.1 contract helpers — Biuro Popytu fields (no network)."""

from __future__ import annotations

import csv
import json
import os
from datetime import date, datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

from agent.demand_os.connectors.allowlist import ACTIVE, load_allowlist
from agent.demand_os.week_ritual import week_plan

CONTRACT_VERSION = "v2.1.1"

ROBOTA = frozenset(
    {
        "MONEY_CHECK",
        "ICP_ASSET",
        "PUBLISH",
        "BLOG",
        "HUNT",
        "PARKED_STOP",
        "REST",
    }
)

CONTRACT_TOP_KEYS = frozenset(
    {
        "ok",
        "gate",
        "tool",
        "desk",
        "marketing",
        "contract_version",
        "robota_dnia",
        "icp_role_week",
        "iso_week",
        "state",
        "week_calendar",
        "shells_line",
        "screen",
        "money_check",
        "dual_cash",
        "data_mode",
        "last_real_event",
        "stl",
        "kpi",
        "footer",
        "cash_warning",
        "diagnostics",
    }
)

_DAY_TO_ROBOTA = {
    "pon": "MONEY_CHECK",
    "wt": "ICP_ASSET",
    "sr": "PUBLISH",
    "czw": "BLOG",
    "pt": "HUNT",
    "sob": "REST",
    "nd": "REST",
}


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def set_now_path() -> Path:
    env = os.environ.get("DEMAND_OS_SET_NOW")
    if env:
        return Path(env)
    return _repo_root() / "docs" / "ops" / "demand-os" / "set-now"


# back-compat
_set_now = set_now_path


def resolve_robota_dnia(
    *,
    marketing: str = "PARKED_LAST",
    day: str = "",
) -> Dict[str, Any]:
    plan = week_plan(day=day)
    d = plan["day"]
    base = _DAY_TO_ROBOTA.get(d, "REST")
    _ROBOTA_LABELS = {
        "MONEY_CHECK": "Sprawdź kasę",
        "ICP_ASSET": "Treść dla ICP",
        "PUBLISH": "Publikuj",
        "BLOG": "Napisz blog",
        "HUNT": "Kontaktuj klientów",
        "REST": "Odpoczynek",
    }
    parked = (marketing or "").upper().startswith("PARKED")
    if parked and base in ("PUBLISH", "BLOG", "HUNT"):
        code = "PARKED_STOP"
        label = _ROBOTA_LABELS.get(base, base)
        note = f"Publikowanie wstrzymane (plan: {label})"
    else:
        code = base
        note = (plan.get("job") or {}).get("title") or _ROBOTA_LABELS.get(code, code)
    return {
        "code": code,
        "day": d,
        "title": note,
        "label": _ROBOTA_LABELS.get(code, code),
        "parked": parked,
        "week_job": plan.get("job"),
    }


def resolve_icp_week(*, set_now: Optional[Path] = None) -> Dict[str, Any]:
    from agent.demand_os.memory import load_memory

    root = set_now or set_now_path()
    mem_path = root / "MEMORY.json"
    store = load_memory(path=mem_path)
    source = "memory" if mem_path.is_file() else "default"
    sem = store.get("semantic") or {}
    role = (sem.get("icp_role_week") or "installateur").strip()
    return {
        "icp_role_week": role or "installateur",
        "hook_nl": sem.get("hook_nl") or "",
        "source": source,
    }


def iso_week_label(*, today: Optional[date] = None) -> str:
    d = today or date.today()
    y, w, _ = d.isocalendar()
    return f"{y}-W{w:02d}"


def desk_state(*, marketing: str = "PARKED_LAST") -> str:
    return "PARKED" if (marketing or "").upper().startswith("PARKED") else "LIVE"


def build_week_calendar() -> List[Dict[str, Any]]:
    out: List[Dict[str, Any]] = []
    for d in ("pon", "wt", "sr", "czw", "pt"):
        p = week_plan(day=d)
        job = p.get("job") or {}
        out.append(
            {
                "day": d,
                "robota": _DAY_TO_ROBOTA[d],
                "title": job.get("title") or d,
            }
        )
    return out


def shells_line() -> str:
    return "Operator: Dowodca | Wave1 shells: status read-only (nie 5 dzialow)"


def _engage_by_target(root: Path) -> Dict[str, Dict[str, Any]]:
    path = root / "ENGAGE-LOG.jsonl"
    latest: Dict[str, Dict[str, Any]] = {}
    if not path.is_file():
        return latest
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rec = json.loads(line)
        except json.JSONDecodeError:
            continue
        tid = str(rec.get("target_id") or "")
        if not tid:
            continue
        latest[tid] = rec
    return latest


def build_hunt_queue(*, set_now: Optional[Path] = None, limit: int = 8) -> List[Dict[str, Any]]:
    """B2 — allowlist + ENGAGE-LOG → READY|SENT|BLOCK."""
    root = set_now or set_now_path()
    path = root / "ALLOWLIST.json"
    if not path.is_file():
        return []
    try:
        data = load_allowlist(path=path)
    except (OSError, ValueError, json.JSONDecodeError):
        return []
    engage = _engage_by_target(root)
    queue: List[Dict[str, Any]] = []
    for t in data["targets"]:
        if t.status == ACTIVE:
            action = "HUNT_COMMENT"
        elif t.is_group:
            action = "JOIN_OR_PREP"
        else:
            continue
        eng = engage.get(t.id) or {}
        if eng:
            if eng.get("ok") is True and eng.get("action") == "comment":
                desk_status = "SENT"
            elif eng.get("ok") is False:
                desk_status = "BLOCK"
            else:
                desk_status = "READY"
        else:
            desk_status = "READY" if t.status == ACTIVE else "JOIN_OR_PREP"
        draft = ""
        if t.status == ACTIVE:
            draft = "1 wartość + 1 wezwanie do Wizard (test)"
        queue.append(
            {
                "target_id": t.id,
                "name": t.name,
                "platform": t.platform,
                "status": t.status,
                "action": action,
                "desk_status": desk_status,
                "draft": draft,
                "cta": "1 wartość + 1 CTA Wizard",
                "engage_notes": (eng.get("notes") or "")[:120],
            }
        )
        if len(queue) >= limit:
            break
    return queue


def dual_cash_report(*, set_now: Optional[Path] = None) -> Dict[str, Any]:
    """D — DA audit FAIL / offerte-only (columns: verdict, offerte_only)."""
    root = set_now or set_now_path()
    path = root / "DA-AUDIT-LOG.csv"
    open_fail = 0
    rows = 0
    if path.is_file():
        with path.open(encoding="utf-8", newline="") as fh:
            for r in csv.DictReader(fh):
                rows += 1
                verdict = (r.get("verdict") or r.get("outcome") or "").upper().strip()
                offerte = (r.get("offerte_only") or "").upper().strip()
                notes = (r.get("notes") or "").lower()
                if verdict == "PASS":
                    continue
                if verdict == "FAIL":
                    open_fail += 1
                    continue
                if offerte in ("Y", "YES", "TRUE", "1") and verdict != "PASS":
                    open_fail += 1
                    continue
                # explicit fail in notes, but not "0 fail"
                if " dual cash = 0 fail" in notes or "0 fail" in notes:
                    continue
                if notes.strip().endswith("fail") or " verdict fail" in notes:
                    open_fail += 1
    return {
        "open_fail": open_fail,
        "audit_rows": rows,
        "rule": "DA → Wizard <24h · offerte ≠ success",
        "red": open_fail > 0,
        "columns": ["verdict", "offerte_only", "wizard_pushed"],
    }


def starts_wow_delta(
    ledger_rows: List[Dict[str, str]],
    *,
    today: Optional[date] = None,
) -> int:
    """Δ wizard_starts this ISO week vs previous (injectable today for tests)."""
    today = today or date.today()
    this_start = today - timedelta(days=today.weekday())
    prev_start = this_start - timedelta(days=7)
    prev_end = this_start - timedelta(days=1)

    def _sum(a: date, b: date) -> int:
        total = 0
        for r in ledger_rows:
            raw = (r.get("date") or "").strip()[:10]
            if not raw:
                continue
            try:
                d = date.fromisoformat(raw)
            except ValueError:
                continue
            if a <= d <= b:
                try:
                    total += int(r.get("wizard_starts") or 0)
                except ValueError:
                    pass
        return total

    return _sum(this_start, today) - _sum(prev_start, prev_end)


def validator_fail_display(*, publish_count: int, validator_fail: int) -> Any:
    if int(publish_count or 0) <= 0:
        return "n/a"
    return int(validator_fail or 0)


def detect_data_mode(
    *,
    set_now: Optional[Path] = None,
    events_path: Optional[Path] = None,
    ledger_rows: Optional[List[Dict[str, str]]] = None,
) -> Dict[str, Any]:
    """FIXTURE / REAL / MIXED / EMPTY — last_real_event only from REAL hits."""
    root = set_now or set_now_path()
    ev = events_path if events_path is not None else (root / "GROWTH-EVENTS.jsonl")
    fixture_hits = 0
    real_hits = 0
    last_ts = ""
    last_type = ""

    rows = ledger_rows
    if rows is None:
        led = root / "LEDGER.csv"
        rows = []
        if led.is_file():
            with led.open(encoding="utf-8", newline="") as fh:
                rows = list(csv.DictReader(fh))

    for r in rows or []:
        notes = (r.get("notes") or "").lower()
        try:
            starts = int(r.get("wizard_starts") or 0)
        except ValueError:
            starts = 0
        pub = (r.get("publish_Y/N") or "").strip().upper() == "Y"
        if not starts and not pub:
            continue
        is_fix = "fixture" in notes or "sample" in notes or "fict" in notes
        if is_fix:
            fixture_hits += 1
            continue
        real_hits += 1
        d = (r.get("date") or "").strip()
        if d >= last_ts:
            last_ts = d
            last_type = "ledger"

    if ev.is_file():
        for line in ev.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line:
                continue
            try:
                rec = json.loads(line)
            except json.JSONDecodeError:
                continue
            notes = (rec.get("notes") or "").lower()
            et = rec.get("event_type") or ""
            if et not in ("wizard_start", "paid", "cta_issued", "bridge_proof"):
                continue
            is_fix = "fixture" in notes or "sample" in notes
            if is_fix:
                fixture_hits += 1
                continue
            real_hits += 1
            ts = str(rec.get("ts") or "")
            if ts >= last_ts:
                last_ts = ts
                last_type = et

    if fixture_hits and real_hits:
        mode = "MIXED"
    elif fixture_hits:
        mode = "FIXTURE"
    elif real_hits:
        mode = "REAL"
    else:
        mode = "EMPTY"

    last_real = {
        "ts": last_ts if real_hits else "",
        "kind": last_type if real_hits else "",
        "stale_warn": _stale_warn(last_ts, mode) if real_hits else (mode == "EMPTY"),
    }
    return {
        "data_mode": mode,
        "fixture_hits": fixture_hits,
        "real_hits": real_hits,
        "last_real_event": last_real,
    }


def _stale_warn(ts: str, mode: str) -> bool:
    if mode in ("EMPTY", "FIXTURE") or not ts:
        return mode == "EMPTY"
    try:
        if "T" in ts:
            dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
            if dt.tzinfo is None:
                dt = dt.replace(tzinfo=timezone.utc)
            age_h = (
                datetime.now(timezone.utc) - dt.astimezone(timezone.utc)
            ).total_seconds() / 3600
        else:
            d = date.fromisoformat(ts[:10])
            age_h = (date.today() - d).days * 24
        return age_h > 48
    except ValueError:
        return False


def top_wizard_assets(
    starts_by_utm: Dict[str, int],
    *,
    limit: int = 5,
) -> List[Dict[str, Any]]:
    ranked = sorted(starts_by_utm.items(), key=lambda kv: kv[1], reverse=True)
    out: List[Dict[str, Any]] = []
    for utm, n in ranked[:limit]:
        asset = (
            utm.rstrip("/").split("utm_content=")[-1].split("&")[0]
            if "utm_content=" in utm
            else utm[-48:]
        )
        channel = ""
        if "utm_source=" in utm:
            channel = utm.split("utm_source=")[-1].split("&")[0]
        out.append(
            {"asset": asset or "unknown", "channel": channel, "starts": int(n), "utm": utm}
        )
    return out


def lightweight_doctor_ok(*, root: Optional[Path] = None) -> bool:
    """Footer slice — required files only (never nest full run_doctor)."""
    repo = root or _repo_root()
    required = (
        "agent/demand_os/desk_contract.py",
        "agent/demand_os/commander_status.py",
        "docs/ops/demand-os/DESK-CONTRACT.md",
        "docs/ops/demand-os/PROGRAM-PHASES.md",
    )
    return all((repo / p).is_file() for p in required)


def build_desk_footer(
    *,
    gate: str,
    data_mode: str,
    last_real: Dict[str, Any],
    doctor_ok: Optional[bool] = None,
    doctor_scope: str = "lightweight",
    doctor_files_ok: Optional[bool] = None,
) -> Dict[str, Any]:
    """Footer honesty: doctor_ok means FULL doctor only when doctor_scope=full.

    Lightweight path never claims PASS via doctor_ok (avoids false green).
    """
    scope = (doctor_scope or "lightweight").strip().lower()
    files_ok = (
        bool(doctor_files_ok)
        if doctor_files_ok is not None
        else lightweight_doctor_ok()
    )
    if scope == "full":
        ok_val = bool(doctor_ok) if doctor_ok is not None else False
    else:
        # Never advertise full PASS from a files-only slice
        ok_val = False
    return {
        "gate": gate,
        "data_mode": data_mode,
        "last_real_event": last_real,
        "stale_warn": bool((last_real or {}).get("stale_warn")),
        "doctor_ok": ok_val,
        "doctor_scope": scope,
        "doctor_files_ok": files_ok,
        "operator": "Dowódca",
        "contract_version": CONTRACT_VERSION,
    }


def format_desk_pretty(status: Dict[str, Any]) -> str:
    """PL one-screen dump (nice-to-have; ASCII-safe for Windows consoles)."""
    r = status.get("robota_dnia") or {}
    kpi = status.get("kpi") or {}
    warn = status.get("cash_warning") or ""
    warn_ascii = warn.replace("€", "EUR")
    title = str(r.get("title") or "").replace("€", "EUR")
    hitl_n = len((status.get("screen") or {}).get("hitl_queue") or [])
    hunt_n = len((status.get("screen") or {}).get("hunt_queue") or [])
    stl_open = (status.get("stl") or {}).get("open_hot")
    dual_fail = (status.get("dual_cash") or {}).get("open_fail")
    lines = [
        f"FLEXGRAFIK | BIURO POPYTU {status.get('desk')} ({status.get('contract_version')})",
        f"Rola tygodnia: {status.get('icp_role_week')}  Stan: {status.get('state')}  "
        f"Tydzien: {status.get('iso_week')}",
        f"* ZADANIE DNIA: {r.get('code')} - {title}",
        f"A PULS: starty={kpi.get('wizard_starts_utm')} dWoW={kpi.get('wizard_starts_wow_delta')} "
        f"platne={kpi.get('paid')} publikacje={kpi.get('publish_count')} "
        f"walidacja={kpi.get('validator_fail')}",
        f"B Tresci do zatwierdzenia: {hitl_n}  Komentarze testowe: {hunt_n}",
        f"D Gorace leady: open={stl_open}  niespojnosc kasy={dual_fail}",
        f"tryb_danych={status.get('data_mode')}  ostrzezenie={warn_ascii}",
        f"shells: {status.get('shells_line')}",
    ]
    return "\n".join(lines)
