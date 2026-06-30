<?php
/**
 * ═══════════════════════════════════════════════════════════════
 * FLEXGRAFIK CHILD THEME - FUNCTIONS.PHP
 * Wersja: 2.0.0 (Clean Architecture)
 * ═══════════════════════════════════════════════════════════════
 */

// Zabezpieczenie przed bezpośrednim dostępem
if (!defined('ABSPATH')) {
    exit;
}

// ═══════════════════════════════════════════════════════════════
// 1. KONFIGURACJA
// ═══════════════════════════════════════════════════════════════

define('FG_VERSION', '2.0.0');
define('FG_DIR', get_stylesheet_directory());
define('FG_URI', get_stylesheet_directory_uri());

// ═══════════════════════════════════════════════════════════════
// 2. ŁADOWANIE MODUŁÓW
// ═══════════════════════════════════════════════════════════════

// WooCommerce: tłumaczenia, shipping, ceny
if (class_exists('WooCommerce')) {
    require_once FG_DIR . '/inc/woocommerce-tweaks.php';
}

// AJAX handlers dla wizarda
require_once FG_DIR . '/inc/ajax-handlers.php';

// Product template data
require_once FG_DIR . '/inc/product-template-data.php';

// ═══════════════════════════════════════════════════════════════
// 3. ENQUEUE SCRIPTS & STYLES
// ═══════════════════════════════════════════════════════════════

add_action('wp_enqueue_scripts', 'fg_enqueue_assets', 20);

function fg_enqueue_assets() {
    
    // ─────────────────────────────────────────
    // A. GLOBALNE STYLE
    // ─────────────────────────────────────────
    wp_enqueue_style(
        'fg-global',
        FG_URI . '/assets/css/zzp-global.css',
        array(),
        FG_VERSION
    );
    
    // ─────────────────────────────────────────
    // B. SEKCJE
    // ─────────────────────────────────────────
    wp_enqueue_style(
        'fg-sections',
        FG_URI . '/assets/css/zzp-sections.css',
        array('fg-global'),
        FG_VERSION
    );
    
    // ─────────────────────────────────────────
    // C. STRONA PRODUKTU (NOWE!)
    // ─────────────────────────────────────────
    if (is_product()) {
        wp_enqueue_style(
            'fg-product',
            FG_URI . '/assets/css/zzp-product.css',
            array('fg-global', 'fg-sections'),
            FG_VERSION
        );
        
        wp_enqueue_script(
            'fg-product',
            FG_URI . '/assets/js/zzp-product.js',
            array('jquery'),
            FG_VERSION,
            true
        );
    }
    
    // ─────────────────────────────────────────
    // D. WIZARD (sklep, produkty)
    // ─────────────────────────────────────────
    if (is_shop() || is_product() || is_woocommerce()) {
        
        wp_enqueue_style(
            'fg-wizard',
            FG_URI . '/assets/css/zzp-wizard.css',
            array(),
            FG_VERSION
        );
        
        wp_enqueue_script(
            'fg-wizard',
            FG_URI . '/assets/js/zzp-wizard.js',
            array('jquery'),
            FG_VERSION,
            true
        );
        
        wp_localize_script('fg-wizard', 'fgWizardConfig', array(
            'ajaxUrl'     => admin_url('admin-ajax.php'),
            'nonce'       => wp_create_nonce('flex_wizard_nonce'),
            'checkoutUrl' => wc_get_checkout_url(),
            'cartUrl'     => wc_get_cart_url(),
            'productMap'  => fg_get_product_map(),
            'i18n'        => array(
                'error'      => 'Er is iets misgegaan.',
                'processing' => 'Verwerken...',
                'addToCart'  => 'Toevoegen',
            )
        ));
    }
    
    // ─────────────────────────────────────────
    // E. STRONY PAKIETÓW
    // ─────────────────────────────────────────
    if (fg_is_package_page()) {
        
        wp_enqueue_style(
            'fg-packages',
            FG_URI . '/assets/css/zzp-packages.css',
            array(),
            FG_VERSION
        );
        
        wp_enqueue_script(
            'fg-packages',
            FG_URI . '/assets/js/zzp-packages.js',
            array('jquery', 'wc-cart-fragments'),
            FG_VERSION,
            true
        );
        
        wp_localize_script('fg-packages', 'fgPackagesConfig', array(
            'ajaxUrl'  => WC_AJAX::get_endpoint('%%endpoint%%'),
            'cartUrl'  => wc_get_cart_url(),
            'currency' => get_woocommerce_currency_symbol(),
            'i18n'     => array(
                'adding' => 'Toevoegen...',
                'added'  => 'Toegevoegd!',
                'error'  => 'Fout. Probeer opnieuw.',
            )
        ));
    }
    
    // ─────────────────────────────────────────
    // F. WOOCOMMERCE CART FRAGMENTS
    // ─────────────────────────────────────────
    if (class_exists('WooCommerce')) {
        wp_enqueue_script('wc-cart-fragments');
    }
}

// ═══════════════════════════════════════════════════════════════
// 4. HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

function fg_is_package_page() {
    $package_pages = array('visible', 'recognizable', 'essential', 'authority');
    
    if (is_page($package_pages)) {
        return true;
    }
    
    $uri = $_SERVER['REQUEST_URI'] ?? '';
    return strpos($uri, '/package/') !== false;
}

function fg_get_product_map() {
    $packages = get_option('zzp_package_ids', array());
    
    if (empty($packages)) {
        $packages = array(
            'VIS-001' => wc_get_product_id_by_sku('VIS-001'),
            'REC-002' => wc_get_product_id_by_sku('REC-002'),
            'ESS-003' => wc_get_product_id_by_sku('ESS-003'),
            'AUT-004' => wc_get_product_id_by_sku('AUT-004'),
        );
    }
    
    $map = array();
    
    foreach ($packages as $sku => $id) {
        if (!$id) continue;
        $map[$id] = (strpos($sku, 'VIS') !== false) ? 'brand' : 'car';
    }
    
    return $map;
}

// ═══════════════════════════════════════════════════════════════
// 5. CUSTOM HEADER & FOOTER
// ═══════════════════════════════════════════════════════════════

add_action('wp_body_open', function() {
    $file = FG_DIR . '/header-custom.php';
    if (file_exists($file)) {
        include $file;
    }
});

add_action('wp_footer', function() {
    $file = FG_DIR . '/footer-custom.php';
    if (file_exists($file)) {
        include $file;
    }
}, 20);

// ═══════════════════════════════════════════════════════════════
// 6. WIZARD MODAL
// ═══════════════════════════════════════════════════════════════

add_action('wp_footer', 'fg_render_wizard_modal', 15);

function fg_render_wizard_modal() {
    if (!is_shop() && !is_product() && !is_woocommerce()) {
        return;
    }
    
    $file = FG_DIR . '/inc/wizard-modal.php';
    if (file_exists($file)) {
        include $file;
    }
}

// ═══════════════════════════════════════════════════════════════
// 7. GLOBAL STYLES (CRITICAL)
// ═══════════════════════════════════════════════════════════════

add_action('wp_head', 'fg_critical_css', 5);

function fg_critical_css() {
    ?>
    <style>
        html, body {
            margin: 0;
            padding: 0;
            overflow-x: hidden;
            background-color: #050505;
        }
        .page-header,
        .entry-header,
        .entry-title {
            display: none !important;
        }
    </style>
    <?php
}
