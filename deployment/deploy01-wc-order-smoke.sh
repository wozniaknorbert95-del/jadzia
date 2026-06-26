#!/usr/bin/env bash
set -euo pipefail
WP="/home/uhqsycwpjz/domains/zzpackage.flexgrafik.nl/public_html"
cd "$WP"

wp eval '
if (!function_exists("wc_create_order")) { echo "NO_WC\n"; return; }
$products = wc_get_products(array("limit"=>1,"status"=>"publish"));
if (empty($products)) { echo "NO_PRODUCT\n"; return; }
$p = $products[0];
$email = "deploy01-int002-" . gmdate("YmdHis") . "@flexgrafik.nl";
$order = wc_create_order();
$order->add_product($p, 1);
$order->set_billing_email($email);
$order->set_billing_first_name("Deploy");
$order->set_billing_last_name("INT002");
$order->set_payment_method("mollie_wc_gateway_ideal");
$order->update_meta_data("_mollie_payment_id", "tr_deploy01_" . time());
$order->calculate_totals();
$order->save();
$oid = $order->get_id();
echo "CREATED order_id=$oid email=$email total=" . $order->get_total() . "\n";
$order->update_status("processing", "DEPLOY-01 E2E synthetic");
echo "STATUS=" . $order->get_status() . "\n";
if (function_exists("fg_jadzia_send_order_webhook")) {
  fg_jadzia_send_order_webhook($order, "processing");
  echo "WEBHOOK_CALLED\n";
} else {
  echo "WEBHOOK_FN_MISSING\n";
}
'

tail -5 "$WP/wp-content/debug.log" 2>/dev/null | grep -i 'FG Jadzia' || echo "no FG Jadzia log lines"
