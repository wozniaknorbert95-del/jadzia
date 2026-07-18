"""Deterministic legacy revenue classification under Revenue Event Contract v1."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, Mapping

Classification = Literal["real", "test", "unknown"]
EntityType = Literal["order", "lead", "portal_qual_lead"]

_TEST_PREFIXES = (
    "deploy01-",
    "deploy02-",
    "int002-e2e-",
    "int004-e2e-",
    "e2e-",
    "smoke-",
)
_TEST_ORDER_PREFIXES = ("smoke-", "deploy-", "e2e-", "test-")
_TEST_PAYMENT_PREFIXES = ("tr_deploy", "tr_test", "tr_mollie_test")


@dataclass(frozen=True)
class ClassificationResult:
    """One deterministic classification decision without raw PII evidence."""

    classification: Classification
    reason_code: str
    evidence: dict[str, Any] = field(default_factory=dict)


def canonical_order_id(value: object) -> str:
    """Normalize the known legacy GA4 `WC-<id>` form to the WC numeric ID."""
    order_id = str(value or "").strip()
    if order_id.lower().startswith("wc-") and order_id[3:].isdigit():
        return order_id[3:]
    return order_id


def _email_local_part(record: Mapping[str, Any]) -> str:
    email = str(record.get("email") or record.get("customer_email") or "").strip().lower()
    return email.split("@", 1)[0]


def _test_signal(record: Mapping[str, Any]) -> tuple[str, str] | None:
    local_part = _email_local_part(record)
    if any(local_part.startswith(prefix) for prefix in _TEST_PREFIXES):
        return "known_test_email_pattern", "email_local_part"

    order_id = str(record.get("order_id") or "").strip().lower()
    if any(order_id.startswith(prefix) for prefix in _TEST_ORDER_PREFIXES):
        return "known_test_order_pattern", "order_id_prefix"

    payment_id = str(record.get("payment_id") or "").strip().lower()
    if any(payment_id.startswith(prefix) for prefix in _TEST_PAYMENT_PREFIXES):
        return "known_test_payment_pattern", "payment_id_prefix"

    session_id = str(record.get("session_id") or "").strip().lower()
    if any(session_id.startswith(prefix) for prefix in _TEST_PREFIXES):
        return "known_test_session_pattern", "session_id_prefix"
    return None


def _classify_order(record: Mapping[str, Any]) -> ClassificationResult:
    signal = _test_signal(record)
    if signal:
        reason, evidence_type = signal
        return ClassificationResult("test", reason, {"matched_rule": evidence_type})

    order_id = str(record.get("order_id") or "").strip()
    normalized_id = canonical_order_id(order_id)
    status = str(record.get("status") or "").strip().lower()
    payment_id = str(record.get("payment_id") or "").strip()
    try:
        total_gross = float(record.get("total_gross") or 0)
    except (TypeError, ValueError):
        total_gross = 0.0

    if total_gross == 0:
        return ClassificationResult(
            "unknown",
            "zero_value_without_explicit_test_evidence",
            {"canonical_order_id": normalized_id},
        )
    if order_id != normalized_id:
        return ClassificationResult(
            "unknown",
            "noncanonical_order_id",
            {"canonical_order_id": normalized_id},
        )
    if not normalized_id.isdigit():
        return ClassificationResult("unknown", "non_numeric_order_id")
    if status not in {"processing", "completed"}:
        return ClassificationResult("unknown", "unconfirmed_order_status")
    if not payment_id:
        return ClassificationResult("unknown", "missing_payment_evidence")
    if total_gross < 199:
        return ClassificationResult(
            "unknown",
            "below_minimum_checkout",
            {"total_gross": total_gross},
        )
    return ClassificationResult(
        "real",
        "production_order_evidence",
        {"canonical_order_id": normalized_id, "total_gross": total_gross},
    )


def _classify_lead(record: Mapping[str, Any]) -> ClassificationResult:
    signal = _test_signal(record)
    if signal:
        reason, evidence_type = signal
        return ClassificationResult("test", reason, {"matched_rule": evidence_type})
    if not _email_local_part(record):
        return ClassificationResult("unknown", "missing_contact_identity")
    return ClassificationResult("unknown", "legacy_lead_requires_human_verification")


def _classify_portal_lead(record: Mapping[str, Any]) -> ClassificationResult:
    signal = _test_signal(record)
    if signal:
        reason, evidence_type = signal
        return ClassificationResult("test", reason, {"matched_rule": evidence_type})
    return ClassificationResult("unknown", "portal_lead_has_no_contact_identity")


def classify_legacy_record(
    entity_type: EntityType,
    record: Mapping[str, Any],
) -> ClassificationResult:
    """Classify a legacy row without mutating it or inferring missing evidence."""
    if entity_type == "order":
        return _classify_order(record)
    if entity_type == "lead":
        return _classify_lead(record)
    if entity_type == "portal_qual_lead":
        return _classify_portal_lead(record)
    raise ValueError(f"unsupported entity_type: {entity_type}")
