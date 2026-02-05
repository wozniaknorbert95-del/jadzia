"""
smart_context.py — Kontekst zależny od typu zadania (oszczędność tokenów).

- classify_task_type(instruction) -> css_only | php_only | template | full
- get_file_map(base_path) -> List[{path, size, role}]
- get_context_for_task(task_type, file_map) -> {system_prompt, planner_context, conventions}

Metryki tokenów (FAZA 3):
- PRZED (pełny kontekst dla "zmień kolor"): ~3000 input tokenów (planer + 50 plików + get_minimal_context).
- PO (smart context css_only): cel ~1000 input tokenów (ok. 60% mniej).
- Pomiar: logi [COST] w agent.py (Input/Output) przy jednym wywołaniu "zmień kolor przycisku".
"""

from typing import List, Dict, Any

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
