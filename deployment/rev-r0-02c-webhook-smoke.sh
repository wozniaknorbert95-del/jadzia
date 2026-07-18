#!/bin/bash
# REV-R0-02C — INT-002 v1 + v2 consumer compatibility smoke (run ON VPS)
set -euo pipefail

JADZIA_ROOT="${JADZIA_ROOT:-/opt/jadzia}"
ENV_FILE="${JADZIA_ROOT}/.env"
DB_PATH="${JADZIA_ROOT}/data/jadzia.db"
BASE="${JADZIA_BASE_URL:-http://127.0.0.1:8000/webhooks/woocommerce/order}"

set -a
# shellcheck disable=SC1091
source "$ENV_FILE"
set +a

: "${WC_WEBHOOK_SECRET:?WC_WEBHOOK_SECRET missing in .env}"

sign() {
  printf '%s' "$1" | openssl dgst -sha256 -hmac "$WC_WEBHOOK_SECRET" | awk '{print $2}'
}

post_payload() {
  local label="$1"
  local body="$2"
  local sig
  sig="$(sign "$body")"
  echo "=== $label ==="
  local resp http body_out
  resp=$(curl -sS -w "\nHTTP:%{http_code}" -X POST "$BASE" \
    -H "Content-Type: application/json" \
    -H "X-WC-Signature: $sig" \
    -d "$body")
  http=$(echo "$resp" | tail -1 | sed 's/HTTP://')
  body_out=$(echo "$resp" | sed '$d')
  echo "HTTP $http"
  echo "$body_out" | python3 -m json.tool 2>/dev/null || echo "$body_out"
  [[ "$http" == "200" ]] || exit 1
  echo "$body_out" | grep -q '"db_status"' || exit 1
}

TS=$(date +%s)
V1_ID="SMOKE-V1-${TS}"
V2_ID="520${TS: -4}"
V2_CHECKOUT="00000000-0000-4000-8000-$(printf '%012d' "$V2_ID")"

V1_BODY=$(cat <<EOF
{"order_id":"${V1_ID}","status":"processing","items":[{"sku":"F-001","qty":1,"price":199}],"customer":{"email":"smoke-v1@test.nl","name":"INT002 v1 Smoke"},"total_gross":199,"payment_id":"tr_smoke_v1_${TS}"}
EOF
)

V2_BODY=$(cat <<EOF
{"schema_version":"int-002.v2","order_id":"${V2_ID}","status":"processing","items":[{"sku":"PKG-GROW","qty":1,"price":199.0}],"customer":{"email":"e2e-revenue@example.test","name":"Revenue Evidence"},"currency":"EUR","total_gross":240.79,"total_net":199.0,"tax_total":41.79,"payment_id":"tr_test_${V2_ID}","payment_status":"paid","payment_method":"mollie_wc_gateway_ideal","payment_provider":"mollie","payment_mode":"test","paid_at":"2026-07-17T18:00:00+00:00","classification":"test","classification_reason":"known_test_email_pattern","is_test":true,"test_reason":"known_test_email_pattern","checkout_id":"${V2_CHECKOUT}","checkout_started_at":"2026-07-17T17:55:00+00:00","checkout_environment":"production","attribution":{"first_touch_source":"email","first_touch_medium":"crm","first_touch_campaign":"rev-r0-02c","first_touch_at":"2026-07-17T17:45:00+00:00","last_touch_source":"email","last_touch_medium":"crm","last_touch_campaign":"rev-r0-02c","last_touch_at":"2026-07-17T17:55:00+00:00","partner_code":null,"wizard_link_id":"rev-r0-02c-${V2_ID}","ga_client_id":null,"utm_source":"email","utm_medium":"crm","utm_campaign":"rev-r0-02c","attribution_status":"partial"}}
EOF
)

post_payload "INT-002 v1 smoke" "$V1_BODY"
post_payload "INT-002 v2 test smoke" "$V2_BODY"

echo "=== DB verify ==="
sqlite3 "$DB_PATH" "SELECT order_id, schema_version, classification, is_test, checkout_id FROM orders WHERE order_id IN ('${V1_ID}','${V2_ID}');"

V1_SCHEMA=$(sqlite3 "$DB_PATH" "SELECT schema_version FROM orders WHERE order_id='${V1_ID}';")
V2_SCHEMA=$(sqlite3 "$DB_PATH" "SELECT schema_version FROM orders WHERE order_id='${V2_ID}';")
V2_CLASS=$(sqlite3 "$DB_PATH" "SELECT classification FROM orders WHERE order_id='${V2_ID}';")

[[ "$V1_SCHEMA" == "int-002.v1" ]] || { echo "FAIL v1 schema_version=$V1_SCHEMA"; exit 1; }
[[ "$V2_SCHEMA" == "int-002.v2" ]] || { echo "FAIL v2 schema_version=$V2_SCHEMA"; exit 1; }
[[ "$V2_CLASS" == "test" ]] || { echo "FAIL v2 classification=$V2_CLASS"; exit 1; }

echo "PASS: INT-002 v1 + v2 consumer compatibility"
