"""Contract tests for deterministic REV-R0-02 legacy classification."""

from agent.revenue.classification import canonical_order_id, classify_legacy_record


def test_known_e2e_lead_is_test():
    result = classify_legacy_record(
        "lead",
        {"email": "int004-e2e-20260717@flexgrafik.nl"},
    )

    assert result.classification == "test"
    assert result.reason_code == "known_test_email_pattern"
    assert "int004-e2e" not in str(result.evidence)


def test_real_order_requires_positive_payment_evidence():
    result = classify_legacy_record(
        "order",
        {
            "order_id": "4201",
            "status": "processing",
            "total_gross": 349.0,
            "payment_id": "tr_live_abc",
            "customer_email": "customer@bouw.nl",
        },
    )

    assert result.classification == "real"
    assert result.reason_code == "production_order_evidence"


def test_zero_value_order_without_explicit_marker_stays_unknown():
    result = classify_legacy_record(
        "order",
        {
            "order_id": "3149",
            "status": "processing",
            "total_gross": 0.0,
            "payment_id": "",
            "customer_email": "unknown@bouw.nl",
        },
    )

    assert result.classification == "unknown"
    assert result.reason_code == "zero_value_without_explicit_test_evidence"


def test_smoke_order_is_test():
    result = classify_legacy_record(
        "order",
        {
            "order_id": "SMOKE-1",
            "status": "processing",
            "total_gross": 299.0,
            "payment_id": "tr_live_abc",
        },
    )

    assert result.classification == "test"


def test_legacy_ga4_prefix_normalizes_but_is_not_assumed_real():
    assert canonical_order_id("WC-4201") == "4201"
    result = classify_legacy_record(
        "order",
        {
            "order_id": "WC-4201",
            "status": "completed",
            "total_gross": 399.0,
            "payment_id": "tr_live_abc",
        },
    )

    assert result.classification == "unknown"
    assert result.reason_code == "noncanonical_order_id"


def test_portal_lead_without_contact_stays_unknown():
    result = classify_legacy_record(
        "portal_qual_lead",
        {"session_id": "portal-session-1", "consent": 1},
    )

    assert result.classification == "unknown"
    assert result.reason_code == "portal_lead_has_no_contact_identity"
