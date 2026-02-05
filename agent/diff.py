"""
diff.py — Generowanie unified diff

Prosty moduł do generowania czytelnych diffów.
"""

import difflib
from typing import Optional


def generate_diff(
    old_content: str,
    new_content: str,
    filename: str,
    context_lines: int = 3
) -> str:
    """
    Generuje unified diff między starą a nową zawartością.
    
    Args:
        old_content: Oryginalna zawartość pliku
        new_content: Nowa zawartość pliku
        filename: Nazwa pliku (do nagłówka diff)
        context_lines: Ile linii kontekstu pokazać
    
    Returns:
        Unified diff jako string
    """
    old_lines = old_content.splitlines(keepends=True)
    new_lines = new_content.splitlines(keepends=True)
    
    # Dodaj newline na końcu jeśli brakuje
    if old_lines and not old_lines[-1].endswith('\n'):
        old_lines[-1] += '\n'
    if new_lines and not new_lines[-1].endswith('\n'):
        new_lines[-1] += '\n'
    
    diff = difflib.unified_diff(
        old_lines,
        new_lines,
        fromfile=f"a/{filename}",
        tofile=f"b/{filename}",
        n=context_lines
    )
    
    return ''.join(diff)


def format_diff_for_display(diff: str, max_lines: int = 50) -> str:
    """
    Formatuje diff do wyświetlenia użytkownikowi.
    
    Dodaje emoji i ogranicza długość.
    """
    if not diff:
        return "Brak zmian w pliku."
    
    lines = diff.split('\n')
    
    formatted = []
    for line in lines[:max_lines]:
        if line.startswith('+++') or line.startswith('---'):
            formatted.append(f"[PLIK] {line}")
        elif line.startswith('@@'):
            formatted.append(f"[LINIA] {line}")
        elif line.startswith('+'):
            formatted.append(f"[+] {line}")
        elif line.startswith('-'):
            formatted.append(f"[-] {line}")
        else:
            formatted.append(f"    {line}")
    
    if len(lines) > max_lines:
        formatted.append(f"\n... i {len(lines) - max_lines} wiecej linii")
    
    return '\n'.join(formatted)


def count_changes(diff: str) -> dict:
    """
    Liczy zmiany w diffie.
    
    Returns:
        {"added": int, "removed": int, "files": int}
    """
    added = 0
    removed = 0
    files = 0
    
    for line in diff.split('\n'):
        if line.startswith('+++'):
            files += 1
        elif line.startswith('+') and not line.startswith('+++'):
            added += 1
        elif line.startswith('-') and not line.startswith('---'):
            removed += 1
    
    return {
        "added": added,
        "removed": removed,
        "files": files
    }


def is_significant_change(diff: str, threshold: int = 100) -> bool:
    """
    Sprawdza czy zmiana jest "duża" (wymaga dodatkowej uwagi).
    """
    changes = count_changes(diff)
    return (changes["added"] + changes["removed"]) > threshold


def create_change_summary(diffs: dict) -> str:
    """
    Tworzy podsumowanie zmian dla wielu plików.
    
    Args:
        diffs: Słownik {filename: diff_string}
    
    Returns:
        Czytelne podsumowanie
    """
    if not diffs:
        return "Brak zmian do pokazania."
    
    summary_lines = ["PODSUMOWANIE ZMIAN", "=" * 40]
    
    total_added = 0
    total_removed = 0
    
    for filename, diff in diffs.items():
        changes = count_changes(diff)
        total_added += changes["added"]
        total_removed += changes["removed"]
        summary_lines.append(
            f"  {filename}: +{changes['added']} / -{changes['removed']}"
        )
    
    summary_lines.append("=" * 40)
    summary_lines.append(f"RAZEM: +{total_added} / -{total_removed} linii")
    
    return '\n'.join(summary_lines)