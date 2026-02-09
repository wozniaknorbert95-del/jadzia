"""
smart_context.py — Kontekst zależny od typu zadania (oszczędność tokenów).

- classify_task_type(instruction) -> css_only | php_only | template | full
- get_file_map(base_path) -> List[{path, size, role}]
- get_context_for_task(task_type, file_map) -> {system_prompt, planner_context, conventions}
- ProjectStructureContext — integracja z project_structure.json (WPExplorer)

Metryki tokenów (FAZA 3):
- PRZED (pełny kontekst dla "zmień kolor"): ~3000 input tokenów (planer + 50 plików + get_minimal_context).
- PO (smart context css_only): cel ~1000 input tokenów (ok. 60% mniej).
- Pomiar: logi [COST] w agent.py (Input/Output) przy jednym wywołaniu "zmień kolor przycisku".
"""

import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from .project_info import (
    PROJECT_INFO,
    get_full_context,
    get_minimal_context,
    CODING_CONVENTIONS_CSS_ONLY,
    CODING_CONVENTIONS_PHP_ONLY,
    WORDPRESS_TIPS,
)


# Słowa kluczowe dla css_only
CSS_KEYWORDS = [
    "zmień kolor", "zmien kolor", "kolor", "css", "style", ".css",
    "tło", "tlo", "font", "czcionka", "padding", "margin", "border",
    "tło", "background", "kolor przycisku", "wygląd przycisku",
    "styl", "style", "arkusz", "nadpisz style",
]

# Słowa kluczowe dla php_only
PHP_KEYWORDS = [
    "funkcja", "funkcję", "hook", "filter", "add_action", "add_filter",
    "functions.php", "wp-content", "woocommerce_", "jadzia_",
]

# Słowa dla template (można traktować jak php_only)
TEMPLATE_KEYWORDS = ["szablon", "template", "template part"]


def classify_task_type(instruction: str) -> str:
    """
    Klasyfikuje typ zadania na podstawie instrukcji (regex/słowa, bez LLM).
    Zwraca: 'css_only' | 'php_only' | 'template' | 'full'
    """
    if not instruction or not instruction.strip():
        return "full"
    lower = instruction.lower().strip()
    # Sprawdź czy w instrukcji jest ścieżka .php
    if ".php" in lower:
        return "php_only"
    for kw in CSS_KEYWORDS:
        if kw in lower:
            return "css_only"
    for kw in TEMPLATE_KEYWORDS:
        if kw in lower:
            return "template"
    for kw in PHP_KEYWORDS:
        if kw in lower:
            return "php_only"
    return "full"


def _role_for_path(path: str) -> str:
    """Określa rolę pliku: style, functions, template."""
    path_lower = path.lower().replace("\\", "/")
    if path_lower.endswith(".css"):
        return "style"
    if "functions.php" in path_lower or path_lower.endswith("functions.php"):
        return "functions"
    if path_lower.endswith(".php"):
        return "template"
    if path_lower.endswith(".html") or path_lower.endswith(".htm"):
        return "template"
    return "other"


def get_file_map(base_path: str) -> List[Dict[str, Any]]:
    """
    Zwraca mapę plików BEZ treści: [{"path": str, "size": int, "role": str}, ...].
    Używa list_files z orchestratora. base_path może służyć do filtrowania (opcjonalnie).
    """
    from agent.tools import list_files
    result = []
    seen = set()
    try:
        for pattern in ["*.css", "*.php"]:
            paths = list_files(pattern)
            for p in paths:
                if p in seen:
                    continue
                seen.add(p)
                if base_path and not p.startswith(base_path.rstrip("/")):
                    continue
                result.append({
                    "path": p,
                    "size": 0,
                    "role": _role_for_path(p),
                })
    except Exception:
        pass
    return result


def get_context_for_task(task_type: str, file_map: List[Dict[str, Any]]) -> Dict[str, str]:
    """
    Zwraca minimalny kontekst dla danego typu zadania:
    { "system_prompt", "planner_context", "conventions" }
    """
    if task_type == "css_only":
        system_prompt = f"""
{PROJECT_INFO}

## ZAKRES
Edytuj TYLKO pliki .css w child theme (style.css itd.). Nie modyfikuj PHP ani konfiguracji.
"""
        paths = [e["path"] for e in file_map if e["role"] == "style"]
        planner_context = "\n".join(paths) if paths else "style.css"
        conventions = f"""
{PROJECT_INFO}

{CODING_CONVENTIONS_CSS_ONLY}
"""
        return {
            "system_prompt": system_prompt.strip(),
            "planner_context": planner_context,
            "conventions": conventions.strip(),
        }

    if task_type == "php_only" or task_type == "template":
        system_prompt = f"""
{PROJECT_INFO}

## ZAKRES
Pliki PHP, hooki, funkcje. Edytuj w child theme (functions.php, szablony).
"""
        paths = [e["path"] for e in file_map if e["role"] in ("functions", "template")]
        planner_context = "\n".join(paths) if paths else "\n".join(e["path"] for e in file_map if e["path"].endswith(".php"))
        if not planner_context:
            planner_context = "functions.php"
        conventions = f"""
{PROJECT_INFO}

{CODING_CONVENTIONS_PHP_ONLY}

{WORDPRESS_TIPS}
"""
        return {
            "system_prompt": system_prompt.strip(),
            "planner_context": planner_context,
            "conventions": conventions.strip(),
        }

    # full
    system_prompt = get_full_context()
    planner_context = "\n".join(e["path"] for e in file_map)
    if not planner_context:
        planner_context = "Brak listy plików"
    conventions = get_minimal_context()
    return {
        "system_prompt": system_prompt,
        "planner_context": planner_context,
        "conventions": conventions,
    }


# ============================================================
# Integration z project_structure.json (WPExplorer)
# ============================================================

logger = logging.getLogger(__name__)


class ProjectStructureContext:
    """
    Kontekst oparty o project_structure.json (generowany przez /skanuj).

    Jeśli plik istnieje — używa task_mappings do wyboru relevantnych plików.
    Jeśli nie — fallback na legacy classify_task_type().
    """

    STRUCTURE_PATH = Path("agent/context/project_structure.json")

    def __init__(self) -> None:
        self.structure: Optional[Dict] = None
        self.available: bool = False
        self._load()

    # ----------------------------------------------------------
    # Loading / reloading
    # ----------------------------------------------------------

    def _load(self) -> None:
        """Ładuje project_structure.json jeśli istnieje."""
        if not self.STRUCTURE_PATH.exists():
            logger.info("project_structure.json not found — using legacy context")
            self.available = False
            self.structure = None
            return

        try:
            with open(self.STRUCTURE_PATH, "r", encoding="utf-8") as f:
                self.structure = json.load(f)

            self.available = True
            logger.info(
                "Loaded project_structure.json: %d files, %d mappings",
                self.structure.get("file_count", 0),
                len(self.structure.get("task_mappings", [])),
            )
        except Exception as e:
            logger.error("Failed to load project_structure.json: %s", e)
            self.available = False
            self.structure = None

    def reload(self) -> None:
        """Wymusza ponowne załadowanie (po /skanuj)."""
        logger.info("Reloading project_structure.json")
        self._load()

    # ----------------------------------------------------------
    # Relevant files for task
    # ----------------------------------------------------------

    def get_relevant_files(self, user_input: str) -> List[str]:
        """
        Zwraca listę plików relevantnych dla zadania.

        Mapuje przez task_mappings[].keywords → files.
        Fallback: critical_files gdy brak dopasowania.
        """
        if not self.available or not self.structure:
            return []

        user_lower = user_input.lower()
        matched_files: set[str] = set()

        for mapping in self.structure.get("task_mappings", []):
            keywords = mapping.get("keywords", [])
            files = mapping.get("files", [])
            for keyword in keywords:
                if keyword.lower() in user_lower:
                    matched_files.update(files)
                    logger.debug("Keyword '%s' matched → %s", keyword, files)
                    break

        if not matched_files:
            critical = self.structure.get("critical_files", [])
            matched_files.update(critical)
            logger.info("No keyword match, using critical_files: %s", critical)

        return list(matched_files)

    # ----------------------------------------------------------
    # File metadata helpers
    # ----------------------------------------------------------

    def get_file_info(self, file_path: str) -> Dict:
        """Zwraca metadane pliku z project_structure.json."""
        if not self.available or not self.structure:
            return {}
        files = self.structure.get("files", {})
        return files.get(file_path, {})

    def get_risk_level(self, file_path: str) -> str:
        """Zwraca risk level dla pliku."""
        info = self.get_file_info(file_path)
        return info.get("risk_level", "medium")

    def needs_backup(self, file_path: str) -> bool:
        """Czy plik wymaga backup przed modyfikacją."""
        if not self.available or not self.structure:
            return True  # bezpiecznie — zawsze backup
        backup_files = self.structure.get("backup_required_files", [])
        return file_path in backup_files

    # ----------------------------------------------------------
    # Hooks summary (for planner context)
    # ----------------------------------------------------------

    def get_hooks_summary(self) -> str:
        """Zwraca krótkie podsumowanie hooków dla kontekstu Claude."""
        if not self.available or not self.structure:
            return ""

        hooks = self.structure.get("hooks", {})
        parts: List[str] = []

        if hooks.get("actions"):
            parts.append(f"Actions: {len(hooks['actions'])}")
        if hooks.get("filters"):
            parts.append(f"Filters: {len(hooks['filters'])}")
        if hooks.get("ajax_handlers"):
            parts.append(f"AJAX handlers: {len(hooks['ajax_handlers'])}")
        if hooks.get("woocommerce_hooks"):
            parts.append(f"WooCommerce hooks: {len(hooks['woocommerce_hooks'])}")

        return ", ".join(parts) if parts else "No hooks data"


# ----------------------------------------------------------
# Singleton
# ----------------------------------------------------------

_project_structure_ctx: Optional[ProjectStructureContext] = None


def get_project_structure_context() -> ProjectStructureContext:
    """Zwraca singleton instancję ProjectStructureContext."""
    global _project_structure_ctx
    if _project_structure_ctx is None:
        _project_structure_ctx = ProjectStructureContext()
    return _project_structure_ctx


def invalidate_project_structure_cache() -> None:
    """Wywołaj po /skanuj aby przeładować strukturę."""
    ctx = get_project_structure_context()
    ctx.reload()
