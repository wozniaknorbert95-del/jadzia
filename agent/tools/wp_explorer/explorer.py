"""
Główna klasa WP Explorer.

Orkiestruje cały proces skanowania projektu WordPress.

Author: Jadzia Architect Team
Version: 1.1
"""

from __future__ import annotations

import asyncio
import logging
import os
import sys
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Literal, Optional

from .config import ExplorerConfig, get_config
from .local_analyzer import LocalAnalyzer
from .models import ProjectStructure, ScanResult
from .ssh_connector import SSHConnector, SSHConnectionError, SSHTimeoutError
from .structure_builder import StructureBuilder

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


def _force_wp_explorer_logging() -> None:
    """
    Force WPExplorer logs to stdout (systemd StandardOutput) and to a dedicated file.
    This bypasses any global INFO-only logging configuration in the main app.
    """
    try:
        root = logging.getLogger()
        if not getattr(root, "_wp_explorer_forced", False):
            # Only configure root if it has no handlers yet (avoid duplicate output).
            if not root.handlers:
                logging.basicConfig(
                    level=logging.DEBUG,
                    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                )
            setattr(root, "_wp_explorer_forced", True)

        log_file = os.getenv("WP_EXPLORER_LOG_FILE")
        if not log_file:
            log_file = "/root/jadzia/logs/wp_explorer.log" if os.name != "nt" else "logs/wp_explorer.log"

        try:
            Path(log_file).parent.mkdir(parents=True, exist_ok=True)
        except Exception:
            pass

        fmt = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

        # stdout handler (goes to logs/jadzia.log via systemd StandardOutput)
        if not any(isinstance(h, logging.StreamHandler) and getattr(h, "stream", None) is sys.stdout for h in logger.handlers):
            sh = logging.StreamHandler(sys.stdout)
            sh.setLevel(logging.DEBUG)
            sh.setFormatter(fmt)
            logger.addHandler(sh)

        # file handler
        if log_file:
            if not any(isinstance(h, logging.FileHandler) and getattr(h, "baseFilename", None) == os.path.abspath(log_file) for h in logger.handlers):
                fh = logging.FileHandler(log_file)
                fh.setLevel(logging.DEBUG)
                fh.setFormatter(fmt)
                logger.addHandler(fh)

        # Avoid double-logging via root handlers.
        logger.propagate = False
        logger.debug("[WP_EXPLORER] Forced logging initialized")
    except Exception:
        # Last resort: never fail import due to logging
        pass


_force_wp_explorer_logging()


class WPExplorer:
    """
    Główna klasa do eksploracji struktury projektu WordPress.
    
    Orkiestruje:
    1. Połączenie SSH i pobranie plików (tar.gz)
    2. Lokalną analizę plików PHP
    3. Budowanie struktury JSON
    4. Zapisywanie wyników
    
    Example:
        explorer = WPExplorer()
        result = await explorer.scan_project()
        
        if result.success:
            print(f"Scanned {result.file_count} files")
    """
    
    def __init__(self, config: Optional[ExplorerConfig] = None):
        """
        Inicjalizuje explorer.
        
        Args:
            config: Konfiguracja (opcjonalna)
        """
        self.config = config or get_config()
        self.ssh = SSHConnector(self.config)
        self.builder = StructureBuilder(self.config)
        self._last_structure: Optional[ProjectStructure] = None
    
    async def scan_project(
        self,
        source: Literal["manual", "post_deploy", "scheduled", "startup"] = "manual",
        trigger_file: Optional[str] = None
    ) -> ScanResult:
        """
        Wykonuje pełne skanowanie projektu WordPress.
        
        Args:
            source: Źródło wywołania skanu
            trigger_file: Plik który wywołał skan (dla post_deploy)
            
        Returns:
            ScanResult z metadanymi skanowania
        """
        start_time = time.time()
        scan_id = uuid.uuid4().hex[:8]
        local_path = self.config.temp_scan_dir / f"scan_{scan_id}"
        
        logger.info(f"Starting project scan (id={scan_id}, source={source})")
        
        errors = []
        warnings = []
        
        try:
            # === PHASE 1: Download ===
            logger.info("Phase 1: Downloading theme files...")
            
            download_result = await self.ssh.download_directory_as_tar(
                self.config.theme_absolute_path,
                local_path
            )
            
            if not download_result.success:
                return ScanResult(
                    success=False,
                    errors=[f"Download failed: {download_result.error}"],
                    source=source,
                    trigger_file=trigger_file,
                    duration_seconds=time.time() - start_time
                )
            
            logger.info(
                f"Downloaded {download_result.file_count} files "
                f"({download_result.size_bytes / 1024:.1f} KB) "
                f"in {download_result.duration_seconds:.1f}s"
            )
            
            # === PHASE 2: Local Analysis ===
            logger.info("Phase 2: Analyzing files locally...")
            
            analyzer = LocalAnalyzer(
                Path(download_result.local_path),
                self.config
            )
            
            # Scan files
            files = analyzer.scan_files()
            
            if not files:
                return ScanResult(
                    success=False,
                    errors=["No files found in theme directory"],
                    source=source,
                    trigger_file=trigger_file,
                    duration_seconds=time.time() - start_time
                )
            
            # Analyze PHP
            analyzer.analyze_php_files()
            
            # === PHASE 3: Build Structure ===
            logger.info("Phase 3: Building project structure...")
            
            scan_duration = time.time() - start_time
            
            structure = self.builder.build(
                files=analyzer.get_files(),
                dependencies=analyzer.get_dependencies(),
                hooks=analyzer.get_hooks(),
                assets=analyzer.get_assets(),
                functions=analyzer.get_functions(),
                scan_duration=scan_duration,
                source=source,
                trigger_file=trigger_file
            )
            
            # === PHASE 4: Save ===
            logger.info("Phase 4: Saving structure...")
            
            output_path = self.builder.save_structure(structure)
            
            # Cache structure
            self._last_structure = structure
            
            # Calculate stats
            hook_count = structure.hooks.total_count
            dynamic_count = len(structure.hooks.dynamic_hooks)
            dep_count = len(structure.dependencies.edges)
            
            duration = time.time() - start_time
            
            logger.info(
                f"Scan completed: {structure.file_count} files, "
                f"{hook_count} hooks ({dynamic_count} dynamic), "
                f"{dep_count} dependencies in {duration:.1f}s"
            )
            
            return ScanResult(
                success=True,
                file_count=structure.file_count,
                hook_count=hook_count,
                dependency_count=dep_count,
                dynamic_hook_count=dynamic_count,
                duration_seconds=round(duration, 2),
                errors=errors,
                warnings=warnings,
                structure_path=output_path,
                source=source,
                trigger_file=trigger_file,
                triggered_at=datetime.now(timezone.utc)
            )
            
        except SSHConnectionError as e:
            logger.error(f"SSH connection error: {e}")
            return ScanResult(
                success=False,
                errors=[f"SSH connection failed: {e}"],
                source=source,
                trigger_file=trigger_file,
                duration_seconds=time.time() - start_time
            )
            
        except SSHTimeoutError as e:
            logger.error(f"SSH timeout: {e}")
            return ScanResult(
                success=False,
                errors=[f"SSH timeout: {e}"],
                source=source,
                trigger_file=trigger_file,
                duration_seconds=time.time() - start_time
            )
            
        except Exception as e:
            logger.exception(f"Unexpected error during scan: {e}")
            return ScanResult(
                success=False,
                errors=[f"Unexpected error: {e}"],
                source=source,
                trigger_file=trigger_file,
                duration_seconds=time.time() - start_time
            )
            
        finally:
            # Cleanup
            await self.ssh.disconnect()
            
            if local_path.exists():
                self.ssh.cleanup_local(local_path)
    
    def get_cached_structure(self) -> Optional[ProjectStructure]:
        """
        Zwraca ostatnio zeskanowaną strukturę z cache.
        
        Returns:
            ProjectStructure lub None
        """
        if self._last_structure:
            return self._last_structure
        
        # Try to load from file
        return self.builder.load_structure()
    
    def invalidate_cache(self) -> None:
        """Unieważnia cache struktury."""
        self._last_structure = None
        logger.info("Structure cache invalidated")


# === AUTO-TRIGGER INTEGRATION ===

class AutoScanTrigger:
    """
    Manager auto-skanowania po deploy.
    
    Zapewnia debounce i zapobiega równoległym skanom.
    """
    
    def __init__(self, config: Optional[ExplorerConfig] = None):
        """Inicjalizuje trigger."""
        self.config = config or get_config()
        self._scan_lock = asyncio.Lock()
        self._last_trigger: Optional[datetime] = None
        self._explorer: Optional[WPExplorer] = None
    
    async def trigger_post_deploy_scan(self, changed_file: str) -> Optional[ScanResult]:
        """
        Triggeruje skan po deploy z debounce.
        
        Args:
            changed_file: Plik który został zmieniony
            
        Returns:
            ScanResult lub None jeśli pominięto
        """
        if not self.config.auto_scan_enabled:
            logger.debug("Auto-scan disabled")
            return None
        
        now = datetime.now(timezone.utc)
        
        # Check debounce
        if self._last_trigger:
            elapsed = (now - self._last_trigger).total_seconds()
            if elapsed < self.config.auto_scan_debounce_seconds:
                logger.info(
                    f"Auto-scan debounced, last trigger {elapsed:.1f}s ago"
                )
                return None
        
        self._last_trigger = now
        
        # Check if scan already running
        if self._scan_lock.locked():
            logger.info("Scan already in progress, skipping trigger")
            return None
        
        # Run scan
        async with self._scan_lock:
            logger.info(f"Auto-scan triggered by deploy of {changed_file}")
            
            if not self._explorer:
                self._explorer = WPExplorer(self.config)
            
            result = await self._explorer.scan_project(
                source="post_deploy",
                trigger_file=changed_file
            )
            
            if result.success:
                logger.info(
                    f"Auto-scan completed: {result.file_count} files, "
                    f"{result.hook_count} hooks"
                )
            else:
                logger.warning(f"Auto-scan failed: {result.errors}")
            
            return result


# Singleton instance for auto-trigger
_auto_trigger: Optional[AutoScanTrigger] = None


def get_auto_trigger() -> AutoScanTrigger:
    """Pobiera singleton instancję AutoScanTrigger."""
    global _auto_trigger
    if _auto_trigger is None:
        _auto_trigger = AutoScanTrigger()
    return _auto_trigger