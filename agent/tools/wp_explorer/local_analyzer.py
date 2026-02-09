"""
Lokalny analizator plików.

Działa na plikach pobranych przez SSH (po tar.gz download).
Znacznie szybszy niż analiza przez sieć.

Author: Jadzia Architect Team
Version: 1.1
"""

from __future__ import annotations

import fnmatch
import logging
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional

from .config import ExplorerConfig, get_config
from .models import (
    Asset,
    Dependency,
    FileInfo,
    FileType,
    FunctionDef,
    Hook,
    RiskLevel,
)
from .php_analyzer import PHPAnalyzer

logger = logging.getLogger(__name__)


class LocalAnalyzer:
    """
    Analizator działający na lokalnych plikach.
    
    Po pobraniu folderu motywu jako tar.gz, analizuje pliki
    lokalnie bez dodatkowych połączeń SSH.
    
    Attributes:
        base_path: Ścieżka do rozpakowanego motywu
        config: Konfiguracja
        php_analyzer: Analizator PHP
    """
    
    # Mapowanie rozszerzeń na FileType
    EXTENSION_MAP = {
        '.php': FileType.PHP,
        '.css': FileType.CSS,
        '.js': FileType.JS,
        '.json': FileType.JSON,
        '.html': FileType.HTML,
        '.htm': FileType.HTML,
    }
    
    def __init__(
        self,
        base_path: Path,
        config: Optional[ExplorerConfig] = None
    ):
        """
        Inicjalizuje analizator.
        
        Args:
            base_path: Ścieżka do rozpakowanego motywu
            config: Konfiguracja (opcjonalna)
        """
        self.base_path = Path(base_path)
        self.config = config or get_config()
        self.php_analyzer = PHPAnalyzer()
        
        # Results storage
        self._files: List[FileInfo] = []
        self._dependencies: List[Dependency] = []
        self._hooks: List[Hook] = []
        self._assets: List[Asset] = []
        self._functions: List[FunctionDef] = []
    
    def _should_ignore(self, path: Path) -> bool:
        """
        Sprawdza czy plik powinien być ignorowany.
        
        Args:
            path: Ścieżka do pliku
            
        Returns:
            True jeśli należy pominąć
        """
        relative_path = str(path.relative_to(self.base_path))
        
        for pattern in self.config.ignore_patterns:
            if fnmatch.fnmatch(relative_path, pattern):
                return True
            if fnmatch.fnmatch(path.name, pattern):
                return True
        
        return False
    
    def _get_file_type(self, path: Path) -> FileType:
        """
        Określa typ pliku na podstawie rozszerzenia.
        
        Args:
            path: Ścieżka do pliku
            
        Returns:
            FileType
        """
        suffix = path.suffix.lower()
        return self.EXTENSION_MAP.get(suffix, FileType.OTHER)
    
    def _get_risk_level(self, relative_path: str) -> RiskLevel:
        """
        Określa poziom ryzyka dla pliku.
        
        Args:
            relative_path: Ścieżka względna
            
        Returns:
            RiskLevel
        """
        # Critical files
        if relative_path in self.config.critical_files:
            return RiskLevel.CRITICAL
        
        # High risk files
        for high_risk in self.config.high_risk_files:
            if relative_path == high_risk or relative_path.endswith(high_risk):
                return RiskLevel.HIGH
        
        # Medium risk - PHP files in inc/
        if relative_path.startswith('inc/') and relative_path.endswith('.php'):
            return RiskLevel.MEDIUM
        
        # Low risk - CSS/JS files
        if relative_path.endswith(('.css', '.js')):
            return RiskLevel.LOW
        
        return RiskLevel.MEDIUM
    
    def _get_file_role(self, relative_path: str, file_type: FileType) -> Optional[str]:
        """
        Określa rolę pliku w projekcie.
        
        Args:
            relative_path: Ścieżka względna
            file_type: Typ pliku
            
        Returns:
            Opis roli lub None
        """
        roles = {
            'functions.php': 'Central hub - loads all inc/ modules',
            'style.css': 'Theme metadata and base styles',
            'header-custom.php': 'Custom header template',
            'footer-custom.php': 'Custom footer template',
            'inc/woocommerce-tweaks.php': 'WooCommerce customizations and translations',
            'inc/checkout-customizer.php': 'Checkout page modifications',
            'inc/ajax-handlers.php': 'AJAX request handlers',
            'inc/upsell-config.php': 'Upsell system configuration',
            'inc/upsell-modal.php': 'Upsell modal template',
            'inc/upsell-ajax-handlers.php': 'Upsell AJAX handlers',
            'inc/wizard-modal.php': 'Product wizard modal',
            'inc/product-template-data.php': 'Product template data',
            'inc/upload-form-handler.php': 'Upload form backend handler',
            'inc/upload-form-template.php': 'Upload form frontend template',
            'inc/upload-token-handler.php': 'Upload security tokens',
            'inc/upload-email-sender.php': 'Upload notification emails',
            'inc/upload-reminder-cron.php': 'Upload reminder CRON job',
            'woocommerce/single-product.php': 'Single product page template override',
        }
        
        if relative_path in roles:
            return roles[relative_path]
        
        # Generic roles
        if relative_path.startswith('assets/css/'):
            return f'Stylesheet for {Path(relative_path).stem.replace("zzp-", "")}'
        
        if relative_path.startswith('assets/js/'):
            return f'JavaScript for {Path(relative_path).stem}'
        
        return None
    
    def scan_files(self) -> List[FileInfo]:
        """
        Skanuje wszystkie pliki w katalogu.
        
        Returns:
            Lista FileInfo dla wszystkich plików
        """
        self._files = []
        file_count = 0
        
        for path in self.base_path.rglob('*'):
            if not path.is_file():
                continue
            
            if self._should_ignore(path):
                continue
            
            # Check file count limit
            file_count += 1
            if file_count > self.config.max_files:
                logger.warning(f"File limit reached: {self.config.max_files}")
                break
            
            # Get file info
            try:
                stat = path.stat()
                size_kb = stat.st_size / 1024
                
                # Skip too large files
                if size_kb > self.config.max_file_size_kb:
                    logger.warning(f"Skipping large file: {path} ({size_kb:.1f} KB)")
                    continue
                
                relative_path = str(path.relative_to(self.base_path))
                file_type = self._get_file_type(path)
                
                file_info = FileInfo(
                    path=relative_path,
                    absolute_path=str(self.config.theme_absolute_path + '/' + relative_path),
                    type=file_type,
                    size_kb=round(size_kb, 2),
                    modified_at=datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc),
                    risk_level=self._get_risk_level(relative_path),
                    role=self._get_file_role(relative_path, file_type)
                )
                
                self._files.append(file_info)
                
            except Exception as e:
                logger.error(f"Error scanning file {path}: {e}")
        
        logger.info(f"Scanned {len(self._files)} files")
        return self._files
    
    def analyze_php_files(self) -> None:
        """
        Analizuje wszystkie pliki PHP.
        
        Wyniki zapisywane są w _dependencies, _hooks, _assets, _functions.
        """
        php_files = [f for f in self._files if f.type == FileType.PHP]
        
        logger.info(f"Analyzing {len(php_files)} PHP files")
        
        for file_info in php_files:
            file_path = self.base_path / file_info.path
            
            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                
                # Analyze
                deps, hooks, assets, funcs = self.php_analyzer.analyze_file(
                    content,
                    file_info.path
                )
                
                self._dependencies.extend(deps)
                self._hooks.extend(hooks)
                self._assets.extend(assets)
                self._functions.extend(funcs)
                
            except Exception as e:
                logger.error(f"Error analyzing {file_info.path}: {e}")
        
        logger.info(
            f"Analysis complete: {len(self._dependencies)} dependencies, "
            f"{len(self._hooks)} hooks, {len(self._assets)} assets"
        )
    
    def get_files(self) -> List[FileInfo]:
        """Zwraca listę przeskanowanych plików."""
        return self._files
    
    def get_dependencies(self) -> List[Dependency]:
        """Zwraca listę zależności."""
        return self._dependencies
    
    def get_hooks(self) -> List[Hook]:
        """Zwraca listę hooków."""
        return self._hooks
    
    def get_assets(self) -> List[Asset]:
        """Zwraca listę assetów."""
        return self._assets
    
    def get_functions(self) -> List[FunctionDef]:
        """Zwraca listę funkcji."""
        return self._functions