"""
Pydantic models dla WP Explorer.

Definiuje wszystkie struktury danych używane w systemie skanowania
struktury projektu WordPress.

Author: Jadzia Architect Team
Version: 1.1
"""

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class FileType(str, Enum):
    """Typy plików rozpoznawane przez skaner."""
    PHP = "php"
    CSS = "css"
    JS = "js"
    JSON = "json"
    HTML = "html"
    OTHER = "other"


class RiskLevel(str, Enum):
    """Poziom ryzyka modyfikacji pliku."""
    CRITICAL = "critical"  # functions.php, style.css - błąd = biały ekran
    HIGH = "high"          # woocommerce-tweaks.php - błąd = broken shop
    MEDIUM = "medium"      # inc/ files - błąd = broken feature
    LOW = "low"            # assets/css/ - błąd = visual only


class FileInfo(BaseModel):
    """Informacje o pojedynczym pliku w projekcie."""
    
    path: str = Field(..., description="Ścieżka względna od roota motywu")
    absolute_path: str = Field(..., description="Pełna ścieżka na serwerze")
    type: FileType = Field(..., description="Typ pliku")
    size_kb: float = Field(..., description="Rozmiar w KB")
    modified_at: Optional[datetime] = Field(None, description="Data ostatniej modyfikacji")
    risk_level: RiskLevel = Field(RiskLevel.MEDIUM, description="Poziom ryzyka")
    role: Optional[str] = Field(None, description="Rola pliku w projekcie")
    
    class Config:
        use_enum_values = True


class Dependency(BaseModel):
    """Zależność między plikami (require/include)."""
    
    source_file: str = Field(..., description="Plik który ładuje")
    target_file: str = Field(..., description="Plik który jest ładowany")
    type: Literal["require", "require_once", "include", "include_once"] = Field(
        ..., description="Typ importu"
    )
    line_number: Optional[int] = Field(None, description="Numer linii")
    raw_statement: Optional[str] = Field(None, description="Oryginalne wyrażenie")


class Hook(BaseModel):
    """WordPress hook (action lub filter)."""
    
    file: str = Field(..., description="Plik zawierający hook")
    type: Literal["action", "filter"] = Field(..., description="Typ hooka")
    hook_name: str = Field(..., description="Nazwa hooka (lub wzorzec dla dynamic)")
    callback_function: Optional[str] = Field(None, description="Funkcja callback")
    priority: int = Field(10, description="Priorytet hooka")
    line_number: Optional[int] = Field(None, description="Numer linii")
    
    # Dynamic hooks support
    is_dynamic: bool = Field(False, description="Czy hook zawiera zmienne")
    dynamic_pattern: Optional[str] = Field(
        None, 
        description="Oryginalny wzorzec z zmiennymi, np. 'order_{$status}'"
    )
    note: Optional[str] = Field(None, description="Dodatkowe informacje")


class Asset(BaseModel):
    """Zarejestrowany asset (CSS/JS) przez wp_enqueue."""
    
    handle: str = Field(..., description="Handle assetu")
    type: Literal["style", "script"] = Field(..., description="Typ assetu")
    path: Optional[str] = Field(None, description="Ścieżka do pliku")
    file: str = Field(..., description="Plik rejestrujący asset")
    dependencies: List[str] = Field(default_factory=list, description="Zależności")
    line_number: Optional[int] = Field(None, description="Numer linii")


class FunctionDef(BaseModel):
    """Definicja funkcji PHP."""
    
    name: str = Field(..., description="Nazwa funkcji")
    file: str = Field(..., description="Plik zawierający funkcję")
    line_number: Optional[int] = Field(None, description="Numer linii")
    is_hooked: bool = Field(False, description="Czy funkcja jest podpięta do hooka")


class HookRegistry(BaseModel):
    """Rejestr wszystkich hooków w projekcie."""
    
    actions: List[Hook] = Field(default_factory=list)
    filters: List[Hook] = Field(default_factory=list)
    ajax_handlers: List[Hook] = Field(default_factory=list)
    woocommerce_hooks: List[Hook] = Field(default_factory=list)
    dynamic_hooks: List[Hook] = Field(default_factory=list)
    
    @property
    def total_count(self) -> int:
        """Łączna liczba hooków."""
        return (
            len(self.actions) + 
            len(self.filters) + 
            len(self.ajax_handlers) + 
            len(self.woocommerce_hooks) +
            len(self.dynamic_hooks)
        )


class DependencyGraph(BaseModel):
    """Graf zależności plików."""
    
    nodes: List[str] = Field(default_factory=list, description="Lista plików")
    edges: List[Dependency] = Field(default_factory=list, description="Lista zależności")
    entry_points: List[str] = Field(
        default_factory=list, 
        description="Pliki ładowane bezpośrednio przez WP"
    )
    load_order: List[str] = Field(
        default_factory=list, 
        description="Kolejność ładowania (topological sort)"
    )


class TaskMapping(BaseModel):
    """Mapowanie zadań na pliki."""
    
    keywords: List[str] = Field(..., description="Słowa kluczowe zadania")
    files: List[str] = Field(..., description="Pliki do modyfikacji")
    risk_level: RiskLevel = Field(..., description="Poziom ryzyka")
    description: Optional[str] = Field(None, description="Opis mapowania")
    
    class Config:
        use_enum_values = True


class ProjectMeta(BaseModel):
    """Metadane projektu."""
    
    name: str = Field(..., description="Nazwa projektu")
    type: Literal["wordpress", "wordpress_woocommerce"] = Field(
        "wordpress_woocommerce"
    )
    architecture: Literal["legacy_child_theme", "fse_block_theme", "classic_theme"] = Field(
        "legacy_child_theme"
    )
    parent_theme: Optional[str] = Field(None, description="Motyw rodzicielski")


class PathConfig(BaseModel):
    """Konfiguracja ścieżek projektu."""
    
    base: str = Field(..., description="Bazowa ścieżka WordPress")
    theme: str = Field(..., description="Ścieżka względna do motywu")
    theme_absolute: str = Field(..., description="Pełna ścieżka do motywu")
    url: str = Field(..., description="URL sklepu")


class ProjectStructure(BaseModel):
    """
    Główna struktura projektu - output WPExplorer.
    
    Ten model reprezentuje kompletny obraz projektu WordPress
    wygenerowany przez skanowanie.
    """
    
    # Metadata
    project: ProjectMeta
    last_scan: datetime
    scan_duration_seconds: float
    scan_source: Literal["manual", "post_deploy", "scheduled", "startup"] = "manual"
    trigger_file: Optional[str] = None
    
    # Paths
    paths: PathConfig
    
    # Files
    files: Dict[str, FileInfo] = Field(default_factory=dict)
    file_count: int = 0
    total_size_kb: float = 0.0
    
    # Analysis
    dependencies: DependencyGraph = Field(default_factory=DependencyGraph)
    hooks: HookRegistry = Field(default_factory=HookRegistry)
    assets: List[Asset] = Field(default_factory=list)
    functions: List[FunctionDef] = Field(default_factory=list)
    
    # Task mapping
    task_mappings: List[TaskMapping] = Field(default_factory=list)
    
    # Safety
    critical_files: List[str] = Field(default_factory=list)
    backup_required_files: List[str] = Field(default_factory=list)
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ScanResult(BaseModel):
    """Wynik skanowania - zwracany do użytkownika."""
    
    success: bool
    file_count: int = 0
    hook_count: int = 0
    dependency_count: int = 0
    dynamic_hook_count: int = 0
    duration_seconds: float = 0.0
    errors: List[str] = Field(default_factory=list)
    warnings: List[str] = Field(default_factory=list)
    structure_path: Optional[str] = None
    
    # Trigger info
    source: Literal["manual", "post_deploy", "scheduled", "startup"] = "manual"
    trigger_file: Optional[str] = None
    triggered_at: datetime = Field(default_factory=lambda: datetime.now())


class DownloadResult(BaseModel):
    """Wynik pobierania katalogu przez SSH."""
    
    success: bool
    local_path: Optional[str] = None
    file_count: int = 0
    size_bytes: int = 0
    duration_seconds: float = 0.0
    error: Optional[str] = None


class CommandResult(BaseModel):
    """Wynik wykonania komendy SSH."""
    
    stdout: str = ""
    stderr: str = ""
    exit_code: int = 0
    duration_seconds: float = 0.0