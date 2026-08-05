"""Worker journal export parser — pure-function contract (9-03)."""

from __future__ import annotations

from tools.demand_os_worker_journal_export import parse_journal, render_markdown

SAMPLE = """2026-08-05T07:15:50+0000 vps systemd[1]: Starting demand-os-agents-worker.service - Demand OS agents worker (run-due dispatch)...
2026-08-05T07:15:53+0000 vps python[101]: {
2026-08-05T07:15:53+0000 vps python[101]:  "ok": true,
2026-08-05T07:15:53+0000 vps python[101]:  "mode": "apply",
2026-08-05T07:15:53+0000 vps python[101]:  "due": [{"role": "sales", "action": "sync_hot"}],
2026-08-05T07:15:53+0000 vps python[101]:  "runs": [
2026-08-05T07:15:53+0000 vps python[101]:   {"role": "sales", "action": "sync_hot", "status": "dispatched", "ok": true, "error": ""}
2026-08-05T07:15:53+0000 vps python[101]:  ],
2026-08-05T07:15:53+0000 vps python[101]:  "dispatched": 1,
2026-08-05T07:15:53+0000 vps python[101]:  "errors": 0
2026-08-05T07:15:53+0000 vps python[101]: }
2026-08-05T07:15:54+0000 vps systemd[1]: demand-os-agents-worker.service: Deactivated successfully.
2026-08-05T07:30:50+0000 vps systemd[1]: Started demand-os-agents-worker.service.
2026-08-05T07:30:53+0000 vps python[102]: {
2026-08-05T07:30:53+0000 vps python[102]:  "ok": true,
2026-08-05T07:30:53+0000 vps python[102]:  "mode": "apply",
2026-08-05T07:30:53+0000 vps python[102]:  "due": [{"role": "validator", "action": "compliance"}],
2026-08-05T07:30:53+0000 vps python[102]:  "runs": [
2026-08-05T07:30:53+0000 vps python[102]:   {"role": "validator", "action": "compliance", "status": "error", "ok": false, "error": "boom"}
2026-08-05T07:30:53+0000 vps python[102]:  ],
2026-08-05T07:30:53+0000 vps python[102]:  "dispatched": 0,
2026-08-05T07:30:53+0000 vps python[102]:  "errors": 1
2026-08-05T07:30:53+0000 vps python[102]: }
2026-08-05T07:30:54+0000 vps systemd[1]: demand-os-agents-worker.service: Failed with result 'exit-code'.
"""


def test_parse_journal_counts_ticks_and_envelopes():
    stats = parse_journal(SAMPLE)
    assert stats["ticks"] == 2
    assert stats["service_failures"] == 1
    assert stats["envelopes"] == 2
    assert stats["dispatched_total"] == 1
    assert stats["errors_total"] == 1
    assert stats["per_role"]["sales/sync_hot"]["dispatched"] == 1
    assert stats["per_role"]["validator/compliance"]["error"] == 1
    assert stats["error_lines"] == ["validator/compliance: boom"]


def test_parse_journal_ignores_non_json_noise():
    stats = parse_journal("2026-08-05T07:15:50+0000 vps systemd[1]: some noise\nno braces here\n")
    assert stats["ticks"] == 0
    assert stats["envelopes"] == 0
    assert stats["per_role"] == {}


def test_render_markdown_contains_summary_and_tail():
    stats = parse_journal(SAMPLE)
    md = render_markdown(stats, "tail-line", since="7 days ago", host="vps")
    assert "| ticków (Started) | 2 |" in md
    assert "| sales/sync_hot | 1 | 0 | 0 |" in md
    assert "validator/compliance: boom" in md
    assert "tail-line" in md
