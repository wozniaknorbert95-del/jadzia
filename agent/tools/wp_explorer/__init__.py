"""
WP Explorer - Automatyczne skanowanie struktury WordPress.

Ten moduł zapewnia narzędzia do:
- Skanowania struktury plików motywu WordPress
- Analizy zależności PHP (require/include)
- Wykrywania hooków WordPress (statycznych i dynamicznych)
- Budowania mapy projektu dla AI agenta

Example:
    from agent.tools.wp_explorer import WPExplorer
    
    explorer = WPExplorer()
    result = await explorer.scan_project()
    
    if result.success:
        print(f"Found {result.file_count} files")
        print(f"Found {result.hook_count} hooks")

Author: Jadzia Architect Team
Version: 1.1
"""

from .config import ExplorerConfig, get_config
from .explorer import AutoScanTrigger, WPExplorer, get_auto_trigger
from .local_analyzer import LocalAnalyzer
from .models import (
    Asset,
    CommandResult,
    Dependency,
    DependencyGraph,
    DownloadResult,
    FileInfo,
    FileType,
    FunctionDef,
    Hook,
    HookRegistry,
    PathConfig,
    ProjectMeta,
    ProjectStructure,
    RiskLevel,
    ScanResult,
    TaskMapping,
)
from .php_analyzer import PHPAnalyzer
from .ssh_connector import (
    SecurityError,
    SSHConnectionError,
    SSHConnector,
    SSHTimeoutError,
)
from .structure_builder import StructureBuilder

__all__ = [
    # Main classes
    "WPExplorer",
    "AutoScanTrigger",
    "get_auto_trigger",
    
    # Config
    "ExplorerConfig",
    "get_config",
    
    # Components
    "SSHConnector",
    "LocalAnalyzer",
    "PHPAnalyzer",
    "StructureBuilder",
    
    # Models
    "ProjectStructure",
    "ScanResult",
    "FileInfo",
    "FileType",
    "RiskLevel",
    "Dependency",
    "DependencyGraph",
    "Hook",
    "HookRegistry",
    "Asset",
    "FunctionDef",
    "TaskMapping",
    "ProjectMeta",
    "PathConfig",
    "DownloadResult",
    "CommandResult",
    
    # Exceptions
    "SSHConnectionError",
    "SSHTimeoutError",
    "SecurityError",
]

__version__ = "1.1.0"