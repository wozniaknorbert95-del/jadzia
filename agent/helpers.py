"""
helpers.py — Funkcje pomocnicze dla agenta

NAPRAWKA #3: Czyszczenie odpowiedzi Claude z markdown code blocks
"""

import logging
import re
from typing import Optional

_log = logging.getLogger(__name__)


def clean_code_response(response: str, language: Optional[str] = None) -> str:
    """
    Usuwa markdown code blocks z odpowiedzi Claude.
    
    Claude często zwraca kod w formacie:
    ```php
    <?php
    // kod
    ?>
    ```
    
    Ta funkcja wyciąga czysty kod.
    
    Args:
        response: Odpowiedź od Claude
        language: Oczekiwany język (php, css, js, html) - opcjonalnie
    
    Returns:
        Czysty kod bez markdown
    """
    cleaned = response.strip()
    
    # Pattern 1: ``` język na początku i ``` na końcu
    # Przykład: ```php\nkod\n```
    if language:
        pattern = rf'^```{language}\s*\n(.*?)\n```\s*$'
    else:
        pattern = r'^```\w*\s*\n(.*?)\n```\s*$'
    
    match = re.search(pattern, cleaned, re.DOTALL | re.MULTILINE)
    if match:
        cleaned = match.group(1)
        _log.debug("Usunięto markdown code block (pattern 1)")
        return cleaned.strip()
    
    # Pattern 2: Tylko ``` na początku i końcu (bez języka)
    # Przykład: ```\nkod\n```
    pattern2 = r'^```\s*\n(.*?)\n```\s*$'
    match2 = re.search(pattern2, cleaned, re.DOTALL | re.MULTILINE)
    if match2:
        cleaned = match2.group(1)
        _log.debug("Usunięto markdown code block (pattern 2)")
        return cleaned.strip()
    
    # Pattern 3: Usuwanie pojedynczych linii z backticks
    # Czasem Claude dodaje ``` na początku ale bez języka
    lines = cleaned.split('\n')
    
    # Usuń pierwszą linię jeśli to ```język lub ```
    if lines and re.match(r'^```\w*\s*$', lines[0]):
        lines = lines[1:]
        _log.debug("Usunięto pierwszą linię markdown")
    
    # Usuń ostatnią linię jeśli to ```
    if lines and lines[-1].strip() == '```':
        lines = lines[:-1]
        _log.debug("Usunięto ostatnią linię markdown")
    
    cleaned = '\n'.join(lines)
    cleaned = _strip_leading_trailing_prose(cleaned.strip(), language)
    
    return cleaned


def _strip_leading_trailing_prose(text: str, language: Optional[str] = None) -> str:
    """
    Usuwa wiodące i końcowe linie wyjaśnień (proza) zostawiając tylko kod.
    """
    if not text:
        return text
    lines = text.split("\n")
    # Wzorce początku kodu (pierwsza znacząca linia)
    code_start_patterns = re.compile(
        r"^\s*(\<\?php|\<\?|\<\!|/\*|//|@import|\.|#|\[|\*|\s*$|"
        r"const |let |var |function |import |export |\')"
    )
    # Proza na końcu (do usunięcia)
    trailing_prose = re.compile(
        r"^\s*(Done\.?|Hope this helps\.?|Here (is|are)\.?|"
        r"Oto (zmieniony|zaktualizowany)\.?|To (wszystko|było)\.?|"
        r"Zaktualizowany plik\.?|Powodzenia\.?)\s*$",
        re.IGNORECASE
    )
    start = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if not stripped:
            continue
        if language == "php" and ("<?php" in stripped or "<? " in stripped or stripped.startswith("<?")):
            start = i
            break
        if language == "css" and (stripped.startswith("@") or stripped.startswith(".") or stripped.startswith("#") or stripped.startswith("*") or stripped.startswith("[")):
            start = i
            break
        if code_start_patterns.match(stripped) or (len(stripped) > 0 and stripped[0] in "<@.#[*/"):
            start = i
            break
    end = len(lines)
    for i in range(len(lines) - 1, start - 1, -1):
        stripped = lines[i].strip()
        if not stripped:
            end = i
            continue
        if trailing_prose.match(stripped):
            end = i
            continue
        break
    result = "\n".join(lines[start:end])
    if start > 0 or end < len(lines):
        _log.debug("Stripped leading/trailing prose: lines 0-%d and %d-%d", start, end, len(lines))
    return result.strip()


def detect_language_from_path(file_path: str) -> Optional[str]:
    """
    Wykrywa język programowania na podstawie rozszerzenia pliku.
    
    Args:
        file_path: Ścieżka do pliku
    
    Returns:
        Nazwa języka (php, css, js, html) lub None
    """
    ext_map = {
        '.php': 'php',
        '.css': 'css',
        '.js': 'javascript',
        '.jsx': 'javascript',
        '.html': 'html',
        '.htm': 'html',
        '.xml': 'xml',
        '.json': 'json',
    }
    
    for ext, lang in ext_map.items():
        if file_path.endswith(ext):
            return lang
    
    return None


def clean_code_for_file(response: str, file_path: str) -> str:
    """
    Czyści odpowiedź Claude dla konkretnego pliku.
    
    Automatycznie wykrywa język na podstawie rozszerzenia.
    
    Args:
        response: Odpowiedź od Claude
        file_path: Ścieżka do pliku
    
    Returns:
        Czysty kod
    """
    language = detect_language_from_path(file_path)
    cleaned = clean_code_response(response, language)
    
    _log.debug("clean_code_for_file: %s", file_path)
    _log.debug("  Wykryty język: %s", language or "unknown")
    _log.debug("  Długość przed: %d znaków", len(response))
    _log.debug("  Długość po:    %d znaków", len(cleaned))
    
    return cleaned


def validate_cleaned_code(original: str, cleaned: str, max_diff_ratio: float = 0.1) -> bool:
    """
    Sprawdza czy wyczyszczony kod jest poprawny.
    
    Jeśli usunięcie markdown skróciło kod o więcej niż 10%, 
    może to oznaczać że coś poszło nie tak.
    
    Args:
        original: Oryginalna odpowiedź
        cleaned: Wyczyszczony kod
        max_diff_ratio: Maksymalny stosunek różnicy długości
    
    Returns:
        True jeśli walidacja przeszła
    """
    if not cleaned:
        _log.warning("Wyczyszczony kod jest pusty!")
        return False
    
    original_len = len(original)
    cleaned_len = len(cleaned)
    
    if cleaned_len > original_len:
        _log.warning("Wyczyszczony kod dłuższy od oryginału? (%d > %d)", cleaned_len, original_len)
        return False
    
    diff_ratio = (original_len - cleaned_len) / original_len
    
    if diff_ratio > max_diff_ratio:
        _log.warning("Usunięto %.1f%% treści - to może być za dużo!", diff_ratio * 100)
        _log.debug("Pierwsze 200 znaków oryginału:")
        _log.debug("%s", original[:200])
        _log.debug("Pierwsze 200 znaków po czyszczeniu:")
        _log.debug("%s", cleaned[:200])
        return False
    
    return True


# ============================================================
# PRZYKŁADY UŻYCIA
# ============================================================

if __name__ == "__main__":
    # Test 1: Standardowy markdown
    test1 = """```php
<?php
function hello() {
    echo "Hello";
}
?>
```"""
    
    result1 = clean_code_response(test1, "php")
    print("Test 1:")
    print(result1)
    print()
    
    # Test 2: Bez języka
    test2 = """```
const x = 10;
console.log(x);
```"""
    
    result2 = clean_code_response(test2)
    print("Test 2:")
    print(result2)
    print()
    
    # Test 3: Już czysty kod (nie powinno nic usunąć)
    test3 = """<?php
function hello() {
    echo "Hello";
}
?>"""
    
    result3 = clean_code_response(test3, "php")
    print("Test 3:")
    print(result3)
