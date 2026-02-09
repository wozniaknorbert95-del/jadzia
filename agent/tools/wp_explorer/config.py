"""
Konfiguracja WP Explorer.

Używa Pydantic BaseSettings do ładowania konfiguracji
z pliku .env lub zmiennych środowiskowych.

Author: Jadzia Architect Team
Version: 1.1
"""

import os
from pathlib import Path
from typing import List, Optional

from dotenv import load_dotenv
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


# Load .env once (zgodnie z patternem w agent/tools/*)
load_dotenv()

# === Module-level defaults (loaded once) ===
_SSH_HOST = os.getenv("SSH_HOST") or os.getenv("CYBERFOLKS_HOST") or "s34.cyber-folks.pl"
_SSH_PORT = int(os.getenv("SSH_PORT") or os.getenv("CYBERFOLKS_PORT") or "222")
_SSH_USER = os.getenv("SSH_USER") or os.getenv("CYBERFOLKS_USER") or "uhqsycwpjz"
_SSH_KEY_PATH = os.getenv("SSH_KEY_PATH") or os.getenv("CYBERFOLKS_KEY_PATH") or "/root/.ssh/wordpress_key"
_WORDPRESS_BASE_PATH = os.getenv("BASE_PATH") or os.getenv("CYBERFOLKS_BASE_PATH") or "/home/user/public_html"


class ExplorerConfig(BaseSettings):
    """
    Konfiguracja WP Explorer.

    Priorytet:
    1) WP_EXPLORER_* (env_prefix)
    2) fallback na globalne zmienne Jadzi: SSH_* / BASE_PATH
    3) twarde defaulty
    """
    
    # === SSH Configuration ===
    ssh_host: str = Field(
        default=_SSH_HOST,
        description="Host SSH WordPress (fallback: SSH_HOST)",
    )
    ssh_port: int = Field(
        default=_SSH_PORT,
        description="Port SSH (fallback: SSH_PORT)",
    )
    ssh_user: str = Field(
        default=_SSH_USER,
        description="Użytkownik SSH (fallback: SSH_USER)",
    )
    ssh_key_path: str = Field(
        default=_SSH_KEY_PATH,
        description="Ścieżka do klucza SSH (fallback: SSH_KEY_PATH)",
    )
    ssh_timeout: int = Field(
        default=120,
        description="Timeout połączenia SSH w sekundach",
    )
    ssh_retry_count: int = Field(
        default=3,
        description="Liczba prób ponowienia połączenia",
    )
    ssh_retry_delay: float = Field(
        default=2.0,
        description="Opóźnienie między próbami w sekundach",
    )
    
    # === WordPress Paths ===
    wordpress_base_path: str = Field(
        default=_WORDPRESS_BASE_PATH,
        description="Bazowa ścieżka WordPress na serwerze (fallback: BASE_PATH)",
    )
    theme_relative_path: str = Field(
        default="wp-content/themes/hello-theme-child-master",
        description="Ścieżka względna do motywu",
    )
    shop_url: str = Field(
        default="https://zzpackage.flexgrafik.nl",
        description="URL sklepu",
    )
    
    # === Local Paths ===
    output_path: str = Field(
        default="agent/context/project_structure.json",
        description="Ścieżka do wyjściowego JSON",
    )
    backup_path: str = Field(
        default="agent/context/project_structure.backup.json",
        description="Ścieżka do backupu JSON",
    )
    temp_dir: str = Field(
        default="/tmp/wp_explorer",
        description="Katalog tymczasowy dla skanów",
    )
    
    # === Scanning Limits ===
    max_file_size_kb: int = Field(
        default=1024,
        description="Maksymalny rozmiar pliku do analizy (KB)",
    )
    max_files: int = Field(
        default=500,
        description="Maksymalna liczba plików do skanowania",
    )
    scan_timeout: int = Field(
        default=300,
        description="Timeout całego skanowania w sekundach",
    )
    
    # === Ignore Patterns ===
    ignore_patterns: List[str] = Field(
        default=[
            "*.tmp",
            "*.bak",
            "*.log",
            "*.swp",
            ".git/*",
            ".svn/*",
            "node_modules/*",
            "vendor/*",
            "*.map",
            ".DS_Store",
            "Thumbs.db",
        ],
        description="Wzorce plików do ignorowania",
    )
    
    # === File Risk Classification ===
    critical_files: List[str] = Field(
        default=[
            "functions.php",
            "style.css",
        ],
        description="Pliki krytyczne (błąd = biały ekran)",
    )
    
    high_risk_files: List[str] = Field(
        default=[
            "inc/woocommerce-tweaks.php",
            "inc/checkout-customizer.php",
        ],
        description="Pliki wysokiego ryzyka",
    )
    
    # === Auto-scan Settings ===
    auto_scan_enabled: bool = Field(
        default=True,
        description="Czy włączony auto-scan po deploy",
    )
    auto_scan_debounce_seconds: int = Field(
        default=10,
        description="Debounce dla auto-scan w sekundach",
    )
    
    # === Task Mappings ===
    # Predefiniowane mapowania zadań na pliki
    default_task_mappings: List[dict] = Field(
        default=[
            {
                "keywords": ["kolor", "color", "barwa", "tło", "background"],
                "files": ["assets/css/zzp-global.css", "style.css"],
                "risk_level": "low",
                "description": "Zmiany kolorystyczne"
            },
            {
                "keywords": ["przycisk", "button", "btn"],
                "files": ["assets/css/zzp-global.css", "assets/css/zzp-product.css"],
                "risk_level": "low",
                "description": "Style przycisków"
            },
            {
                "keywords": ["checkout", "kasa", "zamówienie", "płatność"],
                "files": ["inc/checkout-customizer.php", "inc/woocommerce-tweaks.php"],
                "risk_level": "high",
                "description": "Modyfikacje procesu zamówienia"
            },
            {
                "keywords": ["upsell", "cross-sell", "polecane", "sugerowane"],
                "files": [
                    "inc/upsell-config.php",
                    "inc/upsell-modal.php",
                    "inc/upsell-ajax-handlers.php",
                    "assets/css/zzp-upsell-modal.css"
                ],
                "risk_level": "medium",
                "description": "System upselli"
            },
            {
                "keywords": ["wizard", "kreator", "konfigurator"],
                "files": ["inc/wizard-modal.php", "assets/css/zzp-wizard.css"],
                "risk_level": "medium",
                "description": "Wizard wyboru produktu"
            },
            {
                "keywords": ["upload", "plik", "załącznik", "wgraj"],
                "files": [
                    "inc/upload-form-handler.php",
                    "inc/upload-form-template.php",
                    "inc/upload-token-handler.php",
                    "assets/css/zzp-upload-form.css"
                ],
                "risk_level": "medium",
                "description": "System uploadu plików"
            },
            {
                "keywords": ["produkt", "product", "towar"],
                "files": [
                    "woocommerce/single-product.php",
                    "inc/product-template-data.php",
                    "assets/css/zzp-product.css"
                ],
                "risk_level": "medium",
                "description": "Strona produktu"
            },
            {
                "keywords": ["header", "nagłówek", "menu", "nawigacja"],
                "files": ["header-custom.php"],
                "risk_level": "medium",
                "description": "Nagłówek strony"
            },
            {
                "keywords": ["footer", "stopka"],
                "files": ["footer-custom.php"],
                "risk_level": "medium",
                "description": "Stopka strony"
            },
            {
                "keywords": ["email", "mail", "wiadomość"],
                "files": ["inc/upload-email-sender.php"],
                "risk_level": "medium",
                "description": "Emaile systemowe"
            },
            {
                "keywords": ["cron", "harmonogram", "automatyczny"],
                "files": ["inc/upload-reminder-cron.php"],
                "risk_level": "medium",
                "description": "Zadania CRON"
            },
            {
                "keywords": ["ajax", "dynamiczny", "asynchroniczny"],
                "files": ["inc/ajax-handlers.php", "inc/upsell-ajax-handlers.php"],
                "risk_level": "medium",
                "description": "Handlery AJAX"
            },
            {
                "keywords": ["tłumaczenie", "tekst", "napis", "translate"],
                "files": ["inc/woocommerce-tweaks.php"],
                "risk_level": "medium",
                "description": "Tłumaczenia WooCommerce"
            },
        ],
        description="Domyślne mapowania zadań na pliki",
    )
    
    @property
    def theme_absolute_path(self) -> str:
        """Pełna ścieżka do motywu."""
        return f"{self.wordpress_base_path}/{self.theme_relative_path}"
    
    @property
    def temp_scan_dir(self) -> Path:
        """Katalog tymczasowy dla bieżącego skanu."""
        return Path(self.temp_dir)
    
    model_config = SettingsConfigDict(
        env_prefix="WP_EXPLORER_",
        env_file=".env",
        extra="ignore",
    )


# Singleton instance
_config: Optional[ExplorerConfig] = None


def get_config() -> ExplorerConfig:
    """Pobiera singleton instancję konfiguracji."""
    global _config
    if _config is None:
        _config = ExplorerConfig()
    return _config