"""
guardrails.py — Twarde reguły bezpieczeństwa

Ten moduł definiuje co agent MOŻE i czego NIE MOŻE robić.
Guardrails są sprawdzane w KODZIE, nie polegamy na LLM.
"""

import re
from pathlib import Path
from typing import Tuple, List

# ============================================================
# ŚCIEŻKI ZAKAZANE (regex patterns)
# ============================================================

FORBIDDEN_PATTERNS = [
    r"\.env$",
    r"\.env\..*$",
    r"config\.php$",
    r"wp-config\.php$",
    r"\.htaccess$",
    r"\.htpasswd$",
    r".*\.key$",
    r".*\.pem$",
    r".*\.crt$",
    r"/vendor/.*",
    r"/node_modules/.*",
    r".*\.git/.*",
    r".*\.backup\.\d+$",
    r"wp-includes/.*",
    r"wp-admin/.*",
]

# Ścieżki wymagające PODWÓJNEGO potwierdzenia
SENSITIVE_PATTERNS = [
    r"/config/.*",
    r".*\.sql$",
    r".*database.*\.php$",
    r"functions\.php$",
]


# ============================================================
# OPERACJE
# ============================================================

class OperationType:
    READ = "read"
    WRITE = "write"
    DELETE = "delete"
    DEPLOY = "deploy"
    ROLLBACK = "rollback"


# Operacje wymagające potwierdzenia
CONFIRM_REQUIRED = {
    OperationType.WRITE,
    OperationType.DELETE,
    OperationType.DEPLOY,
    OperationType.ROLLBACK,
}

# Operacje wymagające PODWÓJNEGO potwierdzenia
DOUBLE_CONFIRM_REQUIRED = {
    OperationType.DELETE,
    OperationType.DEPLOY,
}


# ============================================================
# LIMITY
# ============================================================

MAX_FILE_SIZE_BYTES = 1_000_000  # 1 MB
MAX_FILES_PER_OPERATION = 10
MAX_DIFF_LINES = 500


# ============================================================
# FUNKCJE WALIDACJI
# ============================================================

def is_path_forbidden(path: str) -> Tuple[bool, str]:
    """
    Sprawdza czy ścieżka jest zakazana.
    
    Returns:
        (True, reason) jeśli zakazana
        (False, "") jeśli dozwolona
    """
    if not path:
        return True, "Pusta sciezka"
    
    normalized = path.replace("\\", "/").lower()
    
    for pattern in FORBIDDEN_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True, f"Sciezka pasuje do zakazanego wzorca: {pattern}"
    
    return False, ""


def is_path_sensitive(path: str) -> bool:
    """Sprawdza czy ścieżka wymaga podwójnego potwierdzenia"""
    if not path:
        return False
    
    normalized = path.replace("\\", "/").lower()
    
    for pattern in SENSITIVE_PATTERNS:
        if re.search(pattern, normalized, re.IGNORECASE):
            return True
    
    return False


def validate_operation(
    operation: str, 
    paths: List[str]
) -> Tuple[bool, str, bool]:
    """
    Waliduje operację przed wykonaniem.
    
    Returns:
        (allowed, message, needs_double_confirm)
    """
    if not paths:
        return True, "", False
    
    # Sprawdź czy wszystkie ścieżki dozwolone
    for path in paths:
        forbidden, reason = is_path_forbidden(path)
        if forbidden:
            return False, f"ZABLOKOWANO: {path}\nPowod: {reason}", False
    
    # Sprawdź limity
    if len(paths) > MAX_FILES_PER_OPERATION:
        return False, f"Za duzo plikow ({len(paths)} > {MAX_FILES_PER_OPERATION})", False
    
    # Sprawdź czy wymaga potwierdzenia
    needs_confirm = operation in CONFIRM_REQUIRED
    needs_double = operation in DOUBLE_CONFIRM_REQUIRED
    
    # Sprawdź czy któryś plik jest wrażliwy
    for path in paths:
        if is_path_sensitive(path):
            needs_double = True
            break
    
    return True, "", needs_double


def validate_content(content: str, path: str) -> Tuple[bool, str]:
    """
    Waliduje zawartość pliku przed zapisem.
    
    Sprawdza:
    - Rozmiar
    - Potencjalnie niebezpieczne wzorce
    """
    if not content:
        return True, ""
    
    # Rozmiar
    size = len(content.encode('utf-8'))
    if size > MAX_FILE_SIZE_BYTES:
        return False, f"Plik za duzy: {size} bajtow (max {MAX_FILE_SIZE_BYTES})"
    
    # Niebezpieczne wzorce PHP
    dangerous_patterns = [
        (r"eval\s*\(", "eval() jest niebezpieczny"),
        (r"exec\s*\(", "exec() jest niebezpieczny"),
        (r"system\s*\(", "system() jest niebezpieczny"),
        (r"shell_exec\s*\(", "shell_exec() jest niebezpieczny"),
        (r"passthru\s*\(", "passthru() jest niebezpieczny"),
        (r"base64_decode\s*\(\s*\$", "Podejrzane base64_decode ze zmienną"),
    ]
    
    for pattern, reason in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return False, f"Wykryto potencjalnie niebezpieczny kod: {reason}"
    
    return True, ""


def sanitize_commit_message(message: str) -> str:
    """Czyści message dla git commit"""
    if not message:
        return "Update"
    
    # Usuń znaki specjalne
    sanitized = re.sub(r'[^\w\s\-\.\,\:\;\!\?\@\#\(\)ąćęłńóśźżĄĆĘŁŃÓŚŹŻ]', '', message)
    # Ogranicz długość
    if len(sanitized) > 100:
        sanitized = sanitized[:97] + "..."
    
    return sanitized.strip() or "Update"


def check_wordpress_safety(content: str, path: str = "") -> dict:
    """
    Check if PHP code is safe for WordPress.

    Returns:
        {"safe": bool, "reason": str (only if not safe), "warnings": list}
    """
    path_lower = (path or "").lower()
    if not path_lower.endswith(".php"):
        return {"safe": True, "warnings": []}

    dangerous_patterns = [
        (r"eval\s*\(", "eval()"),
        (r"exec\s*\(", "exec()"),
        (r"system\s*\(", "system()"),
        (r"shell_exec\s*\(", "shell_exec()"),
        (r"passthru\s*\(", "passthru()"),
        (r"base64_decode\s*\(\s*\$", "base64_decode with variable"),
    ]
    for pattern, name in dangerous_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            return {"safe": False, "reason": f"Dangerous function detected: {name}"}

    warnings = []
    critical_patterns = [
        (r"remove_action\s*\(\s*['\"]wp_head['\"]", "Usuwanie wp_head może zepsuć stronę"),
        (r"remove_action\s*\(\s*['\"]wp_footer['\"]", "Usuwanie wp_footer może zepsuć stronę"),
    ]
    for pattern, reason in critical_patterns:
        if re.search(pattern, content, re.IGNORECASE):
            warnings.append(reason)

    return {"safe": True, "warnings": warnings}


# ============================================================
# KLASA GUARDRAIL CONTEXT MANAGER
# ============================================================

class GuardedOperation:
    """
    Context manager dla chronionych operacji.
    
    Usage:
        with GuardedOperation("write", ["file.txt"]) as guard:
            if guard.allowed:
                do_stuff()
    """
    
    def __init__(self, operation: str, paths: List[str]):
        self.operation = operation
        self.paths = paths
        self.allowed = False
        self.message = ""
        self.needs_double_confirm = False
    
    def __enter__(self):
        self.allowed, self.message, self.needs_double_confirm = validate_operation(
            self.operation, self.paths
        )
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        pass


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def get_safe_path(base_path: str, relative_path: str) -> str:
    """
    Return a safe absolute path guaranteed to be under ``base_path``.

    Uses ``pathlib.Path.resolve()`` to canonicalize the result and then
    verifies it remains under the resolved base.  This prevents directory
    traversal via ``../``, double-encoding, Unicode tricks, and symlinks.

    Raises:
        PermissionError: if the resolved path escapes ``base_path``.
    """
    if not relative_path:
        return base_path.rstrip("/")

    # Normalize backslashes and strip leading slash so it's treated as relative
    normalized = relative_path.replace("\\", "/").lstrip("/")

    base_resolved = Path(base_path).resolve()
    candidate = (base_resolved / normalized).resolve()

    # Verify the candidate is still under base_path
    try:
        candidate.relative_to(base_resolved)
    except ValueError:
        raise PermissionError(
            f"Path traversal blocked: '{relative_path}' resolves outside base path"
        )

    return str(candidate)


def is_allowed_extension(path: str) -> bool:
    """
    Sprawdza czy rozszerzenie pliku jest dozwolone do edycji.
    """
    allowed_extensions = {
        '.php', '.css', '.js', '.html', '.htm',
        '.tpl', '.json', '.xml', '.txt', '.md',
        '.scss', '.sass', '.less'
    }
    
    ext = Path(path).suffix.lower()
    return ext in allowed_extensions


def summarize_operation(operation: str, paths: List[str]) -> str:
    """
    Tworzy czytelne podsumowanie operacji.
    """
    if not paths:
        return f"Operacja: {operation} (brak plikow)"
    
    if len(paths) == 1:
        return f"Operacja: {operation} na pliku {paths[0]}"
    
    return f"Operacja: {operation} na {len(paths)} plikach: {', '.join(paths[:3])}{'...' if len(paths) > 3 else ''}"