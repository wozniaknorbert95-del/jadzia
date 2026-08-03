"""K12 — desk module import/coverage smoke (branch presence)."""

from __future__ import annotations

import agent.demand_os.commander_status as cs
import agent.demand_os.desk_contract as dc
import agent.demand_os.ga4_adapter as ga4
import agent.demand_os.attribution as attr
import agent.demand_os.sot_reconcile as sot
import agent.demand_os.ledger_export as lex


def test_desk_modules_export_expected_surfaces():
    assert callable(cs.build_demand_os_status)
    assert callable(dc.resolve_robota_dnia)
    assert callable(ga4.fetch_wizard_starts)
    assert callable(attr.ingest_wizard_start_event)
    assert callable(sot.reconcile_dual_sot)
    assert callable(lex.export_ledger)
