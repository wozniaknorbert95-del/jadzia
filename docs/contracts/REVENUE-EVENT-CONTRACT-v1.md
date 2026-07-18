# Revenue Event Contract v1

**Program:** REV-WAR-ROOM  
**Gate:** REV-R0-01  
**Status:** APPROVED — Dowódca 2026-07-17  
**Schema version:** `revenue_event.v1`  
**Owner:** Jadzia COI / Revenue Officer  
**North Star:** paid attributable orders with positive contribution margin

## 1. Purpose and authority

This contract is the canonical business and data definition for the 30-day Revenue War Room. It governs GA4, WooCommerce, Jadzia, Wizard, Portal, Game, Widget, and INSPIRE revenue signals.

Rules:

1. SQLite/Jadzia is the operational revenue ledger; WooCommerce is authoritative for order and payment state.
2. GA4 is an analytics projection, never the authority for paid revenue.
3. Producers may retry. Consumers must be idempotent.
4. Test data is retained and classified, not silently deleted.
5. No KPI may count an event with `is_test=true` or unresolved payment state.
6. No marketing follow-up is authorized solely by lead creation or qualification.
7. This document must be approved before REV-R0-02 or any runtime/schema change.

## 2. Canonical event envelope

Every event has these fields:

| Field | Type | Required | Rule |
|---|---|---:|---|
| `event_id` | UUIDv7/ULID string | yes | Globally unique event occurrence ID; immutable. |
| `event_name` | enum | yes | One of the seven events in section 3. |
| `occurred_at` | RFC 3339 UTC | yes | Business occurrence time from the authoritative producer. |
| `recorded_at` | RFC 3339 UTC | yes | Time Jadzia durably accepted the event. |
| `source_system` | enum | yes | `widget`, `portal`, `game`, `inspire`, `wizard`, `woocommerce`, `jadzia`, `manual`. |
| `source_event_id` | string | yes | Stable producer ID used for deduplication. |
| `lead_id` | string/null | conditional | Canonical Jadzia sales lead ID; required for lead/sales events. |
| `order_id` | string/null | conditional | WooCommerce order ID as a string; required for order events. |
| `session_id` | string/null | no | Source session ID; never used as the sole long-term customer identity. |
| `is_test` | boolean | yes | Explicit classification; defaults are forbidden. |
| `test_reason` | string/null | conditional | Required when `is_test=true`. |
| `attribution` | object | yes | First/last touch data described in section 5; may have explicit unknown values. |
| `consent` | object | yes | Contact/privacy evidence described in section 6. |
| `payload` | object | yes | Event-specific fields from section 3. |
| `schema_version` | string | yes | Exactly `revenue_event.v1` for this contract. |
| `correlation_id` | string | yes | Stable workflow trace across source → Jadzia → side effects. |
| `causation_event_id` | string/null | no | Prior canonical event that caused this event. |

Unknown data is represented explicitly as `null` or `"unknown"` where allowed. Producers must not invent values.

## 3. Canonical events

### 3.1 `lead.created`

Meaning: a contactable or intentionally anonymous demand signal is durably captured for the first time in the unified sales lifecycle.

Required:

- `lead_id`
- `payload.identity_type`: `email|phone|anonymous`
- `payload.source_lead_id`
- `payload.entry_point`: `widget|portal|game|inspire|wizard|manual`
- `payload.contact_present`: boolean
- `payload.lifecycle_stage`: `new`

Emission rule: emit once per canonical lead. A repeated source submission adds activity; it does not create another `lead.created`.

Not equivalent to permission for marketing follow-up.

### 3.2 `lead.qualified`

Meaning: a human or an approved deterministic rule has verified every qualification criterion in section 4.

Required:

- `lead_id`
- `payload.qualified_by`: `human|approved_rule`
- `payload.qualified_by_id`
- `payload.criteria`: object containing all five booleans
- `payload.need_summary`
- `payload.purchase_horizon_days`
- `payload.minimum_purchase_capability_eur`
- `payload.lifecycle_stage`: `qualified`

Emission rule: one event for each transition from not-qualified to qualified. Requalification after a documented disqualification uses a new `source_event_id`.

LLM score, “hot lead”, portal preset, game score, or form completion alone is not qualification.

### 3.3 `sales.contact_attempted`

Meaning: an authorized human or approved workflow attempted a real contact through a named channel.

Required:

- `lead_id`
- `payload.channel`: `phone|email|whatsapp|telegram|in_person|other`
- `payload.actor_type`: `human|approved_automation`
- `payload.actor_id`
- `payload.outcome`: `sent|answered|no_answer|bounced|failed|opted_out`
- `payload.next_action_at`: RFC 3339 UTC or null for a terminal outcome
- consent evidence permitting this channel and purpose

Draft creation, Telegram alert, page view, or unapproved LLM output is not a contact attempt.

### 3.4 `sales.wizard_sent`

Meaning: an authorized actor sent the canonical Wizard URL to the lead as a sales next step.

Required:

- `lead_id`
- `payload.channel`
- `payload.actor_id`
- `payload.wizard_url`
- `payload.link_id`
- `payload.utm_source`, `payload.utm_medium`, `payload.utm_campaign`
- `payload.partner_code`: string/null

The URL must resolve to the approved Wizard entry point. Merely displaying a generic CTA is not enough unless delivery to the lead is auditable.

### 3.5 `checkout.started`

Meaning: the Wizard/checkout created a server-observed checkout attempt for a cart that can reach the €199 minimum.

Required:

- `payload.checkout_id`
- `payload.cart_id`
- `payload.currency`: `EUR`
- `payload.value_gross`
- `payload.items`
- `payload.wizard_link_id`: string/null
- `lead_id`: required when identity is known, otherwise null

Client-only page views are analytics hints, not canonical checkout events. A checkout below €199 is invalid and must not be emitted as canonical.

### 3.6 `order.paid`

Meaning: WooCommerce confirms a real order has a captured/settled payment and is not refunded or test.

Required:

- `order_id`
- `payload.payment_id`
- `payload.payment_status`: `paid`
- `payload.woocommerce_status`: `processing|completed`
- `payload.currency`: `EUR`
- `payload.total_gross`
- `payload.total_net`
- `payload.tax_total`
- `payload.contribution_margin_eur`: number/null until reconciled
- `payload.items`
- `lead_id`: required when resolvable; null must create a reconciliation exception

`processing` or `completed` without independent payment confirmation is insufficient. A free/synthetic order, including historical order `3149`, is not a paid order.

### 3.7 `order.refunded`

Meaning: WooCommerce/payment provider confirms a full or partial refund against a previously paid order.

Required:

- `order_id`
- `payload.refund_id`
- `payload.payment_id`
- `payload.refund_type`: `full|partial`
- `payload.amount_gross`
- `payload.currency`: `EUR`
- `payload.reason_code`: string/null
- `causation_event_id`: the corresponding `order.paid` event when known

Each distinct refund is a distinct event. Revenue KPI is reduced by the confirmed refunded amount.

## 4. Business definitions

### Qualified conversation

A qualified conversation counts only when all are true:

1. **Valid contact:** a real two-way conversation occurred and at least one usable contact route is available.
2. **Geographic fit:** customer is within the supported Netherlands/service area for the requested offer.
3. **Offer fit:** need maps to a current FlexGrafik/ZZPackage product or approved service.
4. **Need and timing:** concrete need is stated and purchase horizon is `≤90` days.
5. **Purchase capability:** customer can purchase at least the mandatory `€199` checkout minimum.

Counting rule: one canonical lead may contribute at most one qualified conversation to the 30-day cohort unless explicitly reopened as a separate opportunity. Bot messages, one-way form submissions, LLM scores, staff/test contacts, and conversations missing any criterion do not count.

### Paid attributable order

A paid attributable order counts only when all are true:

1. Real WooCommerce `order_id`.
2. Payment provider/WooCommerce evidence confirms captured or settled payment.
3. `is_test=false`.
4. Gross total is at least `€199`.
5. Order is not fully refunded.
6. A canonical lead or documented attribution touchpoint links the order to a source.
7. Order is counted once by `order_id`, regardless of webhook retries or status updates.

Partial refunds reduce revenue and contribution margin but do not erase the paid-order count; full refunds remove the order from the successful paid-order KPI and remain visible in gross and refund reporting.

## 5. Attribution contract

`attribution` always contains:

| Field | Rule |
|---|---|
| `first_touch_source` | First known acquisition source; immutable after reliable capture. |
| `first_touch_medium` | First known medium. |
| `first_touch_campaign` | First known campaign or `null`. |
| `first_touch_at` | UTC timestamp or `null`. |
| `last_touch_source` | Most recent eligible touch before conversion. |
| `last_touch_medium` | Most recent eligible medium. |
| `last_touch_campaign` | Most recent campaign or `null`. |
| `last_touch_at` | UTC timestamp or `null`. |
| `partner_code` | Stable referral code or `null`. |
| `wizard_link_id` | Stable sent-link ID or `null`. |
| `ga_client_id` | GA4 client ID or `null`; never a business primary key. |
| `utm_source` | Raw captured UTM or `null`. |
| `utm_medium` | Raw captured UTM or `null`. |
| `utm_campaign` | Raw captured UTM or `null`. |
| `attribution_status` | `known|partial|unknown|conflicted`. |

Priority for paid-order attribution:

1. persisted `wizard_link_id` or partner code carried into checkout/order;
2. canonical lead ID carried into checkout/order;
3. exact normalized contact match with a prior lead and compatible time window;
4. persisted first-party UTM/session touchpoint;
5. `unknown` plus reconciliation exception.

GA4 session/source data may corroborate attribution but may not overwrite stronger first-party evidence.

## 6. Privacy and consent

The `consent` object contains:

| Field | Required | Rule |
|---|---:|---|
| `contact_basis` | yes | `requested_service|contract|consent|legitimate_interest|none|unknown`. |
| `marketing_consent` | yes | `granted|denied|not_asked|withdrawn|unknown`. |
| `consent_scope` | yes | Array of approved purposes/channels; may be empty. |
| `captured_at` | conditional | Required for explicit consent. |
| `captured_via` | conditional | UI/form/version/source that captured consent. |
| `policy_version` | conditional | Required when a policy/notice was shown. |
| `evidence_id` | conditional | Immutable audit reference; required before automated marketing. |

Guardrails:

- Service-request follow-up and marketing follow-up are separate purposes.
- `lead.created` and `lead.qualified` never imply marketing consent.
- `marketing_consent=denied|withdrawn|unknown` blocks automated marketing.
- Contact data and message bodies must not appear in application logs or event IDs.
- Analytics receives pseudonymous identifiers only.
- Retention and deletion rules apply to identity data; non-identifying aggregate evidence may remain.
- Every automated contact requires approved template, segment, channel, purpose, evidence, and idempotency key.

## 7. Test classification

An event is `is_test=true` if any deterministic rule matches:

- explicit producer test flag;
- internal/E2E/test environment;
- known synthetic email/domain, phone, session prefix, order marker, coupon, SKU, or payment mode;
- localhost, preview, CI, smoke, or scripted fixture;
- manual classification with audit reason.

Rules:

1. Explicit test evidence always wins over inferred production evidence.
2. `is_test=false` requires positive production evidence for `order.paid`.
3. Ambiguous historical events are classified `unknown` in reconciliation and excluded from KPI until resolved.
4. Reclassification is append-only/audited: actor, timestamp, old value, new value, reason.
5. Test data remains queryable for QA but is excluded from all Revenue War Room KPI.

## 8. Deduplication and ordering

Canonical uniqueness:

| Event | Dedupe key |
|---|---|
| `lead.created` | canonical `lead_id` |
| `lead.qualified` | `lead_id + qualification_cycle_id` |
| `sales.contact_attempted` | provider/message/call ID, otherwise approved action idempotency key |
| `sales.wizard_sent` | `lead_id + link_id + delivery_id` |
| `checkout.started` | `checkout_id` |
| `order.paid` | `order_id + payment_id + payment_state=paid` |
| `order.refunded` | `order_id + refund_id` |

Processing rules:

- Duplicate delivery returns the existing canonical `event_id`; it creates no side effect.
- A changed payload under an existing dedupe key is a conflict, not a silent overwrite.
- Events may arrive out of order. `occurred_at` controls business order; `recorded_at` controls ingestion audit.
- `order.paid` may arrive before lead resolution; it remains valid with an attribution exception.
- `order.refunded` without a known paid event is quarantined for reconciliation, not discarded.

## 9. System mapping

| Canonical concept | WooCommerce / Wizard | GA4 | Jadzia AS-IS | Contract requirement |
|---|---|---|---|---|
| Lead identity | source-dependent | pseudonymous user/client | `leads.email`; portal has session only; widget TTL | Create canonical `lead_id`; identity may be unresolved but durable. |
| Lead created | form/game/widget/portal action | `lead_captured` aggregate | INT-004 durable; portal partial; widget ephemeral | Emit only after durable capture. |
| Qualification | no authority | none | scores/preset/hot alerts | Store verified criteria and actor; scores alone do not qualify. |
| Wizard sent | URL/CTA | campaign/session hints | not canonical | Persist `link_id`, delivery, UTM, partner code. |
| Checkout started | checkout/cart server state | recommended `begin_checkout` projection | absent | Persist first-party `checkout_id`; project to GA4. |
| Paid order | WC order + payment evidence | recommended `purchase` with `transaction_id=order_id` | INT-002 stores processing/completed, total, payment ID | Require payment confirmation and canonical `order.paid`. |
| Refund | WC refund/payment evidence | recommended `refund` with `transaction_id=order_id` | absent | Persist distinct refund events and reverse revenue. |
| Test flag | test mode/order metadata | event parameter/user property for filtering | task test mode exists; revenue tables lack classification | Persist explicit `is_test` and audit reason on every event. |
| Attribution | checkout/order metadata | source/medium/campaign/client ID | aggregate snapshots only | Persist first-party touchpoints and copy them to order. |

GA4 projection:

- `lead.created` → `generate_lead` only when product analytics needs it; include no PII.
- `checkout.started` → `begin_checkout`.
- `order.paid` → `purchase`, with GA4 `transaction_id` exactly equal to WooCommerce `order_id`.
- `order.refunded` → `refund`, with the same `transaction_id`.
- `is_test=true` events must be excluded through deterministic event parameters/data filters and never enter board KPI.

## 10. Valid and invalid examples

### Valid qualified conversation

A Rotterdam contractor speaks with a sales operator, provides a reachable phone/email, needs vehicle lettering within 30 days, fits the current offer, and confirms a budget above €199. The operator verifies all criteria and records the next action.

### Invalid qualified conversation

- Widget says “price?” and receives an AI score of 80, but no contact or two-way human conversation exists.
- Portal recommends a preset, but stores only `session_id` and no usable contact.
- Internal employee completes the Game during E2E.
- Prospect needs an unsupported service or cannot buy within 90 days.

### Valid paid attributable order

WooCommerce order `3150` totals €399, carries a persisted Wizard link/UTM, payment is captured, webhook retry produces one canonical `order.paid`, and `is_test=false`.

### Invalid paid attributable order

- Synthetic/free order `3149` with `total_gross=0.00`.
- Order is `processing` but payment confirmation is absent.
- GA4 reports purchase revenue but no matching WooCommerce order exists.
- Test payment or known E2E identity.
- Duplicate webhook for an already counted `order_id + payment_id`.

## 11. Acceptance gate for REV-R0-01

Approval confirms:

- [ ] seven canonical events and envelope fields are accepted;
- [ ] qualified conversation definition is accepted;
- [ ] paid attributable order definition is accepted;
- [ ] test and deduplication rules are accepted;
- [ ] consent/contact guardrails are accepted;
- [ ] GA4 ↔ WooCommerce ↔ Jadzia authority and mapping are accepted;
- [ ] unknown/conflicted data is excluded until reconciled;
- [ ] runtime implementation may proceed with `REV-R0-02`.

Approval record:

```text
DECISION: APPROVE | CHANGES_REQUESTED
APPROVER: Norbert Wozniak
APPROVED_AT:
NOTES:
```

Until `DECISION: APPROVE` is recorded, this contract is non-executable and REV-R0-02 remains blocked.
