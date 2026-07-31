"""VF-VHQ-W5 Operations Bus — schema, emit, API, approval hooks."""

from __future__ import annotations

import os
from contextlib import contextmanager
from unittest.mock import patch

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from api.app import create_app

JWT_SECRET_VALUE = "test-secret-ops-bus"


@contextmanager
def jwt_env():
    with patch.dict(os.environ, {"JWT_SECRET": JWT_SECRET_VALUE}, clear=False), patch(
        "api.dependencies.JWT_SECRET",
        JWT_SECRET_VALUE,
    ):
        yield


@pytest.fixture
def temp_db(monkeypatch):
    import tempfile

    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    monkeypatch.setattr("agent.db.DB_PATH", path)
    import agent.db as db_mod

    if hasattr(db_mod._local, "conn") and db_mod._local.conn:
        db_mod._local.conn.close()
        db_mod._local.conn = None
    yield path
    try:
        os.unlink(path)
    except OSError:
        pass


@pytest.fixture
def client():
    return TestClient(create_app())


def _auth_headers(role: str = "dowodca") -> dict[str, str]:
    token = pyjwt.encode(
        {"sub": "norbert", "role": role},
        JWT_SECRET_VALUE,
        algorithm="HS256",
    )
    return {"Authorization": f"Bearer {token}"}


def test_ops_bus_schema_and_idempotent_emit(temp_db):
    from agent.db import get_connection
    from agent.ops_bus import emit_ops_bus_event

    get_connection()  # init schema
    r1 = emit_ops_bus_event(
        event_type="lead_qualified",
        source_room="sales-room",
        dest_room="wizard-quote",
        payload_ref="1",
        source_system="jadzia",
        source_event_id="lead_disp:1:acked",
        correlation_id="corr:lead:1",
        payload={"lead_id": 1, "qualified_by": "human"},
        approval_level="L1",
        actor_id="test",
        evidence_id="EV-W5-001",
    )
    assert r1.ok and r1.event_id and not r1.duplicate
    r2 = emit_ops_bus_event(
        event_type="lead_qualified",
        source_room="sales-room",
        dest_room="wizard-quote",
        payload_ref="1",
        source_system="jadzia",
        source_event_id="lead_disp:1:acked",
        correlation_id="corr:lead:1",
        payload={"lead_id": 1},
        approval_level="L1",
        actor_id="test",
    )
    assert r2.ok and r2.duplicate and r2.event_id == r1.event_id


def test_ops_bus_rejects_unknown_type_and_chat_payload(temp_db):
    from agent.db import get_connection
    from agent.ops_bus import emit_ops_bus_event

    get_connection()
    bad = emit_ops_bus_event(
        event_type="agent_chat",
        source_room="sales-room",
        dest_room="wizard-quote",
        payload_ref="x",
        source_system="jadzia",
        source_event_id="x1",
        correlation_id="c1",
    )
    assert not bad.ok
    chat = emit_ops_bus_event(
        event_type="lead_qualified",
        source_room="sales-room",
        dest_room="wizard-quote",
        payload_ref="1",
        source_system="jadzia",
        source_event_id="chat1",
        correlation_id="c1",
        payload={"message": "hello agent"},
        approval_level="L1",
    )
    assert not chat.ok
    assert "forbidden" in (chat.error or "")


def test_ops_bus_flag_off_noop(temp_db):
    from agent.db import get_connection
    from agent.ops_bus import emit_ops_bus_event, set_ops_bus_enabled
    from agent.db import db_ops_bus_list

    get_connection()
    set_ops_bus_enabled(False)
    r = emit_ops_bus_event(
        event_type="lead_qualified",
        source_room="sales-room",
        dest_room="wizard-quote",
        payload_ref="9",
        source_system="jadzia",
        source_event_id="off1",
        correlation_id="corr:lead:9",
        approval_level="L1",
    )
    assert r.ok and r.skipped
    assert db_ops_bus_list(limit=10) == []
    set_ops_bus_enabled(True)


def test_ops_bus_l2_pending_and_l3_stop(temp_db):
    from agent.commander.audit import verify_audit_chain
    from agent.db import db_ops_bus_get_by_event_id, db_ops_bus_list, get_connection
    from agent.ops_bus import emit_ops_bus_event, set_approval_state

    get_connection()
    r = emit_ops_bus_event(
        event_type="lead_qualified",
        source_room="sales-room",
        dest_room="wizard-quote",
        payload_ref="2",
        source_system="jadzia",
        source_event_id="l2test:2",
        correlation_id="corr:lead:2",
        payload={"lead_id": 2, "qualified_by": "human"},
        approval_level="L2",
        actor_id="test",
        evidence_id="EV-W5-005",
    )
    assert r.ok
    assert r.approval_state == "pending"
    assert r.approval_needed_id
    companions = db_ops_bus_list(event_type="approval_needed", limit=20)
    assert any(c["event_id"] == r.approval_needed_id for c in companions)

    stop = emit_ops_bus_event(
        event_type="order_created",
        source_room="wizard-quote",
        dest_room="order-desk",
        payload_ref="WC-L3",
        source_system="test",
        source_event_id="l3:WC-L3",
        correlation_id="corr:order:WC-L3",
        payload={"order_id": "WC-L3"},
        approval_level="L3",
        actor_id="test",
    )
    assert not stop.ok
    assert "L3_requires_founder_go" in (stop.error or "")
    assert stop.approval_needed_id
    # parent order_created must NOT exist as executable row
    orders = db_ops_bus_list(event_type="order_created", limit=20)
    assert not any(o.get("source_event_id") == "l3:WC-L3" for o in orders)
    stop_row = db_ops_bus_get_by_event_id(stop.approval_needed_id)
    assert stop_row is not None
    assert stop_row["approval_level"] == "L3"
    assert stop_row["approval_state"] == "pending"
    deny = set_approval_state(
        event_id=stop.approval_needed_id,
        new_state="approved",
        actor_id="test",
        actor_role="dowodca",
    )
    assert not deny.ok
    assert deny.error == "L3_forbidden"

    chain = verify_audit_chain()
    assert chain.get("valid") is True


def test_sales_cta_spawn_emits_lead_qualified_and_wizard_started(temp_db):
    from agent.db import db_create_lead, db_ops_bus_list
    from agent.nodes.brief_node import collect_weekly_metrics, spawn_brief_sales_cta_tickets

    lead_id, status = db_create_lead(
        {
            "email": "opsbus-cta@test.nl",
            "name": "CTA",
            "source": "widget",
            "consent_status": True,
            "game_score": 55,
        }
    )
    assert status == "success"
    metrics = collect_weekly_metrics()
    ids = spawn_brief_sales_cta_tickets(metrics=metrics)
    assert len(ids) == 1
    ticket_id = ids[0]
    quals = db_ops_bus_list(event_type="lead_qualified", limit=20)
    wiz = db_ops_bus_list(event_type="wizard_started", limit=20)
    assert any(q.get("source_event_id") == f"sales_cta:{ticket_id}" for q in quals)
    assert any(w.get("source_event_id") == f"wiz_cta:{ticket_id}" for w in wiz)
    assert any(w.get("correlation_id") == f"corr:lead:{lead_id}" for w in wiz)


def test_lead_disposition_acked_emits_lead_qualified(client, temp_db):
    from agent.db import db_create_lead, db_ops_bus_list

    lead_id, status = db_create_lead(
        {
            "email": "opsbus.lead@test.nl",
            "name": "Ops",
            "source": "web",
            "consent_status": True,
            "game_score": 85,
            "reward_tier": None,
        }
    )
    assert status == "success"
    with jwt_env():
        r = client.post(
            f"/api/v1/commander/leads/{lead_id}/disposition",
            headers=_auth_headers(),
            json={"disposition": "acked"},
        )
    assert r.status_code == 200
    rows = db_ops_bus_list(event_type="lead_qualified", limit=20)
    assert any(x.get("source_event_id") == f"lead_disp:{lead_id}:acked" for x in rows)


def test_order_webhook_emits_order_created_once(client, temp_db):
    from agent.db import db_ops_bus_list

    payload = {
        "order_id": "WC-OPS-1",
        "status": "completed",
        "items": [{"sku": "PKG-GROW", "qty": 1, "price": 199.0}],
        "customer": {"email": "buyer@ops.nl", "name": "Buyer"},
        "total_gross": 199.0,
        "payment_id": "tr_ops_1",
    }
    r1 = client.post("/webhooks/woocommerce/order", json=payload)
    assert r1.status_code == 200
    rows = db_ops_bus_list(event_type="order_created", limit=20)
    assert len([x for x in rows if x["payload_ref"] == "WC-OPS-1"]) == 1

    payload["status"] = "processing"
    r2 = client.post("/webhooks/woocommerce/order", json=payload)
    assert r2.status_code == 200
    rows2 = db_ops_bus_list(event_type="order_created", limit=20)
    assert len([x for x in rows2 if x["payload_ref"] == "WC-OPS-1"]) == 1


def test_ops_bus_api_list_ingest_approval(client, temp_db):
    from agent.db import get_connection
    from agent.ops_bus import emit_ops_bus_event

    get_connection()
    with jwt_env():
        empty = client.get(
            "/api/v1/commander/ops-bus/events",
            headers=_auth_headers("viewer"),
        )
        assert empty.status_code == 200
        assert empty.json()["total"] == 0

        ingest = client.post(
            "/api/v1/commander/ops-bus/ingest",
            headers=_auth_headers(),
            json={
                "event_type": "wizard_started",
                "lead_id": 42,
                "wizard_deeplink": "https://zzpackage.flexgrafik.nl/wizard/",
            },
        )
        assert ingest.status_code == 200
        assert ingest.json()["ok"] is True

        chat_payload = client.post(
            "/api/v1/commander/ops-bus/ingest",
            headers=_auth_headers(),
            json={
                "event_type": "wizard_started",
                "lead_id": 99,
                "payload": {"message": "free-form agent chat"},
            },
        )
        assert chat_payload.status_code == 422

        # viewer cannot ingest
        denied = client.post(
            "/api/v1/commander/ops-bus/ingest",
            headers=_auth_headers("viewer"),
            json={"event_type": "wizard_started", "lead_id": 1},
        )
        assert denied.status_code == 403

        l2 = emit_ops_bus_event(
            event_type="lead_qualified",
            source_room="sales-room",
            dest_room="wizard-quote",
            payload_ref="77",
            source_system="jadzia",
            source_event_id="api-l2:77",
            correlation_id="corr:lead:77",
            payload={"lead_id": 77},
            approval_level="L2",
            actor_id="test",
        )
        assert l2.ok and l2.event_id
        appr = client.post(
            f"/api/v1/commander/ops-bus/events/{l2.event_id}/approval",
            headers=_auth_headers(),
            json={"state": "approved"},
        )
        assert appr.status_code == 200
        assert appr.json()["side_effects"] is False

        # L3 row inserted directly → 403 on approve
        from agent.db import db_ops_bus_insert
        import uuid

        eid = str(uuid.uuid4())
        db_ops_bus_insert(
            {
                "event_id": eid,
                "event_type": "approval_needed",
                "source_room": "mission-control",
                "dest_room": "approval-vault",
                "payload_ref": "deploy",
                "payload_json": {"go_type": "deploy"},
                "approval_level": "L3",
                "approval_state": "pending",
                "evidence_id": "EV-W5-005",
                "correlation_id": "corr:stop:1",
                "source_system": "test",
                "source_event_id": "manual-l3-1",
                "actor_id": "test",
            }
        )
        forbid = client.post(
            f"/api/v1/commander/ops-bus/events/{eid}/approval",
            headers=_auth_headers(),
            json={"state": "approved"},
        )
        assert forbid.status_code == 403


def test_ops_bus_api_flag_off_empty(client, temp_db):
    from agent.ops_bus import set_ops_bus_enabled

    set_ops_bus_enabled(False)
    with jwt_env():
        r = client.get(
            "/api/v1/commander/ops-bus/events",
            headers=_auth_headers(),
        )
    assert r.status_code == 200
    body = r.json()
    assert body["enabled"] is False
    assert body["events"] == []
    set_ops_bus_enabled(True)


def test_ops_bus_vault_pending_filter_and_l2_companion_approve(client, temp_db):
    """W6 vault contract: pending approval_needed list + L2 companion approve."""
    from agent.db import db_ops_bus_list, get_connection
    from agent.ops_bus import emit_ops_bus_event

    get_connection()
    parent = emit_ops_bus_event(
        event_type="lead_qualified",
        source_room="sales-room",
        dest_room="wizard-quote",
        payload_ref="w6-1",
        source_system="test",
        source_event_id="w6-vault:1",
        correlation_id="corr:w6:1",
        payload={"lead_id": 901},
        approval_level="L2",
        actor_id="test",
    )
    assert parent.ok and parent.approval_needed_id

    with jwt_env():
        pending = client.get(
            "/api/v1/commander/ops-bus/events",
            headers=_auth_headers(),
            params={
                "approval_state": "pending",
                "type": "approval_needed",
                "limit": 40,
            },
        )
        assert pending.status_code == 200
        body = pending.json()
        assert body["enabled"] is True
        ids = {e["event_id"] for e in body["events"]}
        assert parent.approval_needed_id in ids
        # companions only — not the parent lead_qualified row
        assert parent.event_id not in ids

        appr = client.post(
            f"/api/v1/commander/ops-bus/events/{parent.approval_needed_id}/approval",
            headers=_auth_headers(),
            json={"state": "approved"},
        )
        assert appr.status_code == 200
        assert appr.json()["side_effects"] is False

        after = client.get(
            "/api/v1/commander/ops-bus/events",
            headers=_auth_headers(),
            params={"approval_state": "pending", "type": "approval_needed"},
        )
        assert parent.approval_needed_id not in {
            e["event_id"] for e in after.json()["events"]
        }

    companions = db_ops_bus_list(event_type="approval_needed", limit=20)
    row = next(c for c in companions if c["event_id"] == parent.approval_needed_id)
    assert row["approval_state"] == "approved"
