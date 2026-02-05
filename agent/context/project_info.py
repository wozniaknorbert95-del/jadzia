"""
project_info.py — Wiedza o projekcie (dawniej context.py)

Zawiera informacje o projekcie, konwencje i funkcje get_full_context / get_minimal_context.
"""

# ============================================================
# PODSTAWOWE INFORMACJE O PROJEKCIE
# ============================================================

PROJECT_INFO = """
NAZWA PROJEKTU: Sklep WooCommerce
TECHNOLOGIA: WordPress + WooCommerce
MOTYW: Hello Elementor + Hello Elementor Child
WERSJA PHP: 7.4 lub 8.1
BAZA DANYCH: MySQL
SERWER: CyberFolks (Apache)
"""

# ============================================================
# STRUKTURA KATALOGÓW
# ============================================================

DIRECTORY_STRUCTURE = """
/public_html/
├── index.php                 # Główny entry point WordPress
├── wp-config.php             # Konfiguracja WP (NIE EDYTOWAĆ)
├── .htaccess                 # Konfiguracja Apache (NIE EDYTOWAĆ)
│
├── wp-content/
│   ├── themes/
│   │   ├── hello-elementor/           # Motyw główny (NIE EDYTOWAĆ)
│   │   └── hello-elementor-child/     # Motyw child (TUTAJ EDYTUJEMY)
│   │       ├── style.css              # Style child theme
│   │       ├── functions.php          # Funkcje PHP
│   │       └── templates/             # Szablony custom
│   │
│   ├── plugins/                       # Wtyczki (NIE EDYTOWAĆ bezpośrednio)
│   │   └── woocommerce/
│   │
│   └── uploads/                       # Media (tylko odczyt)
│
└── wp-includes/                       # Core WP (NIE EDYTOWAĆ)
"""

# ============================================================
# KONWENCJE KODOWANIA
# ============================================================

CODING_CONVENTIONS = """
## PHP (WordPress)
- Standard: WordPress Coding Standards
- Zmienne: snake_case
- Funkcje: snake_case z prefixem (np. jadzia_get_products)
- Klasy: PascalCase
- Hooki: add_action, add_filter
- Indentacja: tabulatory (nie spacje)
- Encoding: UTF-8

## CSS
- Metodologia: BEM gdzie możliwe
- Nazwy klas: kebab-case
- Używaj zmiennych CSS dla kolorów
- Mobile-first approach

## JavaScript
- ES6+ gdzie możliwe
- jQuery dostępne globalnie (WordPress)
- Nazwy funkcji: camelCase

## Ogólne
- Komentarze w języku polskim lub angielskim
- Każdy plik kończy się pustą linią
- Nie hardkoduj URL-i (użyj get_site_url(), home_url())
"""

# Fragment tylko CSS (dla smart context css_only)
CODING_CONVENTIONS_CSS_ONLY = """
## CSS
- Metodologia: BEM gdzie możliwe
- Nazwy klas: kebab-case
- Używaj zmiennych CSS dla kolorów
- Mobile-first approach
- Edytuj TYLKO pliki .css w child theme
"""

# Fragment PHP + WordPress (dla smart context php_only)
CODING_CONVENTIONS_PHP_ONLY = """
## PHP (WordPress)
- Standard: WordPress Coding Standards
- Zmienne: snake_case
- Funkcje: snake_case z prefixem (np. jadzia_get_products)
- Hooki: add_action, add_filter
- Indentacja: tabulatory (nie spacje)
- Encoding: UTF-8
"""

# ============================================================
# KOLORY I BRANDING
# ============================================================

BRANDING = """
KOLORY (dostosuj do swojego sklepu):
- Primary: #FF5722
- Secondary: #2196F3
- Success: #4CAF50
- Warning: #FFC107
- Error: #F44336
- Text: #212121
- Background: #FFFFFF

FONTY:
- Nagłówki: dziedziczone z Elementor
- Body: dziedziczone z Elementor
"""

# ============================================================
# PLIKI KRYTYCZNE (NIE EDYTOWAĆ)
# ============================================================

CRITICAL_FILES = """
NIGDY nie edytuj tych plików bez wyraźnego polecenia:
- wp-config.php — konfiguracja WordPress i bazy danych
- .htaccess — konfiguracja serwera
- wp-includes/* — core WordPress
- wp-content/plugins/* — pliki wtyczek (edytuj przez panel WP)
- hello-elementor/* — motyw główny (używaj child theme!)
"""

# ============================================================
# TYPOWE LOKALIZACJE DLA ZADAŃ
# ============================================================

TASK_FILE_MAPPING = """
ZADANIE → GDZIE SZUKAĆ

"Zmień styl strony"
→ wp-content/themes/hello-elementor-child/style.css

"Dodaj funkcję PHP"
→ wp-content/themes/hello-elementor-child/functions.php

"Zmień nagłówek/stopkę"
→ Elementor (panel WP) lub functions.php z hookami

"Zmień wygląd produktu WooCommerce"
→ wp-content/themes/hello-elementor-child/woocommerce/

"Dodaj custom CSS"
→ wp-content/themes/hello-elementor-child/style.css
→ lub Elementor → Custom CSS

"Zmień tekst/tłumaczenie"
→ functions.php z filtrem gettext
→ lub pliki .po/.mo
"""

# ============================================================
# WORDPRESS/WOOCOMMERCE HELPERS
# ============================================================

WORDPRESS_TIPS = """
## Przydatne hooki WooCommerce:
- woocommerce_before_main_content
- woocommerce_after_main_content
- woocommerce_before_single_product
- woocommerce_after_single_product
- woocommerce_before_cart
- woocommerce_after_cart

## Przydatne funkcje:
- get_site_url() - URL strony
- home_url() - URL strony głównej
- get_template_directory_uri() - URL motywu
- get_stylesheet_directory_uri() - URL child theme
- wc_get_products() - pobierz produkty
- WC()->cart - obiekt koszyka
"""

# ============================================================
# FUNKCJE DO POBIERANIA KONTEKSTU
# ============================================================

def get_full_context() -> str:
    """Zwraca pełny kontekst projektu dla prompta"""
    return f"""
{PROJECT_INFO}

## STRUKTURA PROJEKTU
{DIRECTORY_STRUCTURE}

## KONWENCJE KODOWANIA
{CODING_CONVENTIONS}

## BRANDING
{BRANDING}

## PLIKI KRYTYCZNE
{CRITICAL_FILES}

## MAPOWANIE ZADAŃ NA PLIKI
{TASK_FILE_MAPPING}

## WSKAZÓWKI WORDPRESS/WOOCOMMERCE
{WORDPRESS_TIPS}
"""


def get_minimal_context() -> str:
    """Zwraca minimalny kontekst (dla oszczędności tokenów)"""
    return f"""
{PROJECT_INFO}

## KLUCZOWE ZASADY
- Edytuj TYLKO w hello-elementor-child/
- NIE ruszaj: wp-config.php, .htaccess, wp-includes/
- Używaj WordPress Coding Standards
- Prefikuj funkcje: jadzia_*

## GŁÓWNE PLIKI DO EDYCJI
- style.css - style CSS
- functions.php - funkcje PHP, hooki
- woocommerce/ - nadpisania szablonów WC
"""
