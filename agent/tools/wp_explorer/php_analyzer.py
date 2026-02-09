"""
Analizator kodu PHP z obsługą dynamic hooks.

Wykrywa:
- require/include statements
- add_action/add_filter (statyczne i dynamiczne)
- wp_enqueue_style/script
- Definicje funkcji

Author: Jadzia Architect Team
Version: 1.1
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import List, Optional, Tuple

from .models import Asset, Dependency, FunctionDef, Hook

logger = logging.getLogger(__name__)


class PHPAnalyzer:
    """
    Analizator kodu PHP dla WordPress.
    
    Używa wyrażeń regularnych do parsowania kodu PHP bez wykonywania go.
    Obsługuje zarówno statyczne jak i dynamiczne hooki WordPress.
    
    Example:
        analyzer = PHPAnalyzer()
        hooks = analyzer.find_hooks(php_content, "functions.php")
        deps = analyzer.find_requires(php_content, "functions.php")
    """
    
    # === STATIC PATTERNS ===
    # Hooki ze stałymi stringami
    
    REQUIRE_PATTERNS = {
        # require_once 'file.php';
        'simple_string': re.compile(
            r"(require|require_once|include|include_once)\s*"
            r"[\(\s]*['\"]([^'\"]+)['\"][\)\s]*;",
            re.IGNORECASE
        ),
        # require_once get_stylesheet_directory() . '/inc/file.php';
        'get_stylesheet': re.compile(
            r"(require|require_once|include|include_once)\s*"
            r"[\(\s]*get_stylesheet_directory\s*\(\s*\)\s*\.\s*['\"]([^'\"]+)['\"][\)\s]*;",
            re.IGNORECASE
        ),
        # require_once get_template_directory() . '/inc/file.php';
        'get_template': re.compile(
            r"(require|require_once|include|include_once)\s*"
            r"[\(\s]*get_template_directory\s*\(\s*\)\s*\.\s*['\"]([^'\"]+)['\"][\)\s]*;",
            re.IGNORECASE
        ),
        # require_once __DIR__ . '/inc/file.php';
        'dir_const': re.compile(
            r"(require|require_once|include|include_once)\s*"
            r"[\(\s]*__DIR__\s*\.\s*['\"]([^'\"]+)['\"][\)\s]*;",
            re.IGNORECASE
        ),
        # require_once dirname(__FILE__) . '/inc/file.php';
        'dirname_file': re.compile(
            r"(require|require_once|include|include_once)\s*"
            r"[\(\s]*dirname\s*\(\s*__FILE__\s*\)\s*\.\s*['\"]([^'\"]+)['\"][\)\s]*;",
            re.IGNORECASE
        ),
    }
    
    HOOK_PATTERNS = {
        # add_action('hook_name', 'callback');
        'add_action': re.compile(
            r"add_action\s*\(\s*['\"]([a-zA-Z0-9_]+)['\"]\s*,\s*"
            r"['\"]?([a-zA-Z0-9_]+)['\"]?"
            r"(?:\s*,\s*(\d+))?",  # Optional priority
            re.IGNORECASE
        ),
        # add_filter('filter_name', 'callback');
        'add_filter': re.compile(
            r"add_filter\s*\(\s*['\"]([a-zA-Z0-9_]+)['\"]\s*,\s*"
            r"['\"]?([a-zA-Z0-9_]+)['\"]?"
            r"(?:\s*,\s*(\d+))?",
            re.IGNORECASE
        ),
    }
    
    # === DYNAMIC PATTERNS ===
    # Hooki ze zmiennymi w nazwie
    
    DYNAMIC_HOOK_PATTERNS = {
        # add_action("hook_{$var}", ...);
        'action_interpolated': re.compile(
            r"add_action\s*\(\s*[\"']([^\"']*\{\$[^}]+\}[^\"']*)[\"']",
            re.IGNORECASE
        ),
        # add_filter("filter_{$var}", ...);
        'filter_interpolated': re.compile(
            r"add_filter\s*\(\s*[\"']([^\"']*\{\$[^}]+\}[^\"']*)[\"']",
            re.IGNORECASE
        ),
        # do_action("hook_{$var}");
        'do_action_interpolated': re.compile(
            r"do_action\s*\(\s*[\"']([^\"']*\{\$[^}]+\}[^\"']*)[\"']",
            re.IGNORECASE
        ),
        # apply_filters("filter_{$var}", ...);
        'apply_filters_interpolated': re.compile(
            r"apply_filters\s*\(\s*[\"']([^\"']*\{\$[^}]+\}[^\"']*)[\"']",
            re.IGNORECASE
        ),
        # add_action("hook_" . $var, ...);
        'action_concat': re.compile(
            r"add_action\s*\(\s*[\"']([^\"']+)[\"']\s*\.\s*\$(\w+)",
            re.IGNORECASE
        ),
        # add_filter("filter_" . $var, ...);
        'filter_concat': re.compile(
            r"add_filter\s*\(\s*[\"']([^\"']+)[\"']\s*\.\s*\$(\w+)",
            re.IGNORECASE
        ),
    }
    
    ENQUEUE_PATTERNS = {
        # wp_enqueue_style('handle', get_stylesheet_directory_uri() . '/path.css');
        'enqueue_style': re.compile(
            r"wp_enqueue_style\s*\(\s*['\"]([^'\"]+)['\"]\s*"
            r"(?:,\s*(?:get_stylesheet_directory_uri\s*\(\s*\)\s*\.\s*)?['\"]([^'\"]*)['\"])?"
        ),
        # wp_enqueue_script('handle', get_stylesheet_directory_uri() . '/path.js');
        'enqueue_script': re.compile(
            r"wp_enqueue_script\s*\(\s*['\"]([^'\"]+)['\"]\s*"
            r"(?:,\s*(?:get_stylesheet_directory_uri\s*\(\s*\)\s*\.\s*)?['\"]([^'\"]*)['\"])?"
        ),
    }
    
    FUNCTION_PATTERN = re.compile(
        r"function\s+([a-zA-Z_][a-zA-Z0-9_]*)\s*\(",
        re.IGNORECASE
    )
    
    # Pattern to detect comments
    COMMENT_PATTERNS = {
        'single_line': re.compile(r'//.*$', re.MULTILINE),
        'multi_line': re.compile(r'/\*.*?\*/', re.DOTALL),
    }
    
    def __init__(self):
        """Inicjalizuje analizator."""
        self._hooked_functions: set = set()
    
    def _remove_comments(self, content: str) -> str:
        """
        Usuwa komentarze z kodu PHP.
        
        Args:
            content: Kod PHP
            
        Returns:
            Kod bez komentarzy
        """
        # Remove multi-line comments first
        content = self.COMMENT_PATTERNS['multi_line'].sub('', content)
        # Then single-line
        content = self.COMMENT_PATTERNS['single_line'].sub('', content)
        return content
    
    def _get_line_number(self, content: str, position: int) -> int:
        """
        Zwraca numer linii dla pozycji w tekście.
        
        Args:
            content: Pełny tekst
            position: Pozycja znaku
            
        Returns:
            Numer linii (1-indexed)
        """
        return content[:position].count('\n') + 1
    
    def _normalize_path(self, raw_path: str) -> str:
        """
        Normalizuje ścieżkę z PHP do względnej.
        
        Args:
            raw_path: Surowa ścieżka (może zaczynać się od /)
            
        Returns:
            Znormalizowana ścieżka względna
        """
        # Remove leading slash if present
        path = raw_path.lstrip('/')
        # Remove ./ prefix
        if path.startswith('./'):
            path = path[2:]
        return path
    
    def find_requires(
        self,
        content: str,
        file_path: str
    ) -> List[Dependency]:
        """
        Znajduje wszystkie require/include w pliku PHP.
        
        Args:
            content: Zawartość pliku PHP
            file_path: Ścieżka pliku (do kontekstu)
            
        Returns:
            Lista znalezionych zależności
        """
        # Remove comments
        clean_content = self._remove_comments(content)
        
        dependencies = []
        
        for pattern_name, pattern in self.REQUIRE_PATTERNS.items():
            for match in pattern.finditer(clean_content):
                require_type = match.group(1).lower()
                raw_path = match.group(2)
                
                # Normalize path
                target_file = self._normalize_path(raw_path)
                
                # Skip if empty or invalid
                if not target_file or target_file.startswith('$'):
                    continue
                
                line_number = self._get_line_number(content, match.start())
                
                dependencies.append(Dependency(
                    source_file=file_path,
                    target_file=target_file,
                    type=require_type,
                    line_number=line_number,
                    raw_statement=match.group(0)[:100]  # Truncate for logging
                ))
                
                logger.debug(
                    f"Found {require_type}: {file_path} -> {target_file} "
                    f"(line {line_number})"
                )
        
        return dependencies
    
    def find_hooks(
        self,
        content: str,
        file_path: str
    ) -> List[Hook]:
        """
        Znajduje wszystkie hooki - statyczne i dynamiczne.
        
        Args:
            content: Zawartość pliku PHP
            file_path: Ścieżka pliku
            
        Returns:
            Lista hooków
        """
        clean_content = self._remove_comments(content)
        hooks = []
        
        # === STATIC HOOKS ===
        for pattern_name, pattern in self.HOOK_PATTERNS.items():
            hook_type = 'action' if 'action' in pattern_name else 'filter'
            
            for match in pattern.finditer(clean_content):
                hook_name = match.group(1)
                callback = match.group(2)
                priority = int(match.group(3)) if match.lastindex >= 3 and match.group(3) else 10
                
                line_number = self._get_line_number(content, match.start())
                
                # Track hooked functions
                self._hooked_functions.add(callback)
                
                hooks.append(Hook(
                    file=file_path,
                    type=hook_type,
                    hook_name=hook_name,
                    callback_function=callback,
                    priority=priority,
                    line_number=line_number,
                    is_dynamic=False
                ))
        
        # === DYNAMIC HOOKS ===
        for pattern_name, pattern in self.DYNAMIC_HOOK_PATTERNS.items():
            hook_type = 'action' if 'action' in pattern_name else 'filter'
            
            for match in pattern.finditer(clean_content):
                dynamic_pattern = match.group(1)
                
                # Create base name by replacing variables with *
                base_name = re.sub(r'\{\$\w+\}', '*', dynamic_pattern)
                base_name = re.sub(r'\$\w+$', '*', base_name)  # For concatenation
                
                line_number = self._get_line_number(content, match.start())
                
                hooks.append(Hook(
                    file=file_path,
                    type=hook_type,
                    hook_name=base_name,
                    callback_function=None,
                    line_number=line_number,
                    is_dynamic=True,
                    dynamic_pattern=dynamic_pattern,
                    note="Dynamic hook - actual name determined at runtime"
                ))
        
        return hooks
    
    def find_enqueues(
        self,
        content: str,
        file_path: str
    ) -> List[Asset]:
        """
        Znajduje wszystkie wp_enqueue_style i wp_enqueue_script.
        
        Args:
            content: Zawartość pliku PHP
            file_path: Ścieżka pliku
            
        Returns:
            Lista assetów
        """
        clean_content = self._remove_comments(content)
        assets = []
        
        for pattern_name, pattern in self.ENQUEUE_PATTERNS.items():
            asset_type = 'style' if 'style' in pattern_name else 'script'
            
            for match in pattern.finditer(clean_content):
                handle = match.group(1)
                path = match.group(2) if match.lastindex >= 2 else None
                
                # Normalize path
                if path:
                    path = self._normalize_path(path)
                
                line_number = self._get_line_number(content, match.start())
                
                assets.append(Asset(
                    handle=handle,
                    type=asset_type,
                    path=path,
                    file=file_path,
                    line_number=line_number
                ))
        
        return assets
    
    def find_functions(
        self,
        content: str,
        file_path: str
    ) -> List[FunctionDef]:
        """
        Znajduje wszystkie definicje funkcji.
        
        Args:
            content: Zawartość pliku PHP
            file_path: Ścieżka pliku
            
        Returns:
            Lista definicji funkcji
        """
        clean_content = self._remove_comments(content)
        functions = []
        
        for match in self.FUNCTION_PATTERN.finditer(clean_content):
            func_name = match.group(1)
            line_number = self._get_line_number(content, match.start())
            
            # Check if function is hooked
            is_hooked = func_name in self._hooked_functions
            
            functions.append(FunctionDef(
                name=func_name,
                file=file_path,
                line_number=line_number,
                is_hooked=is_hooked
            ))
        
        return functions
    
    def analyze_file(
        self,
        content: str,
        file_path: str
    ) -> Tuple[List[Dependency], List[Hook], List[Asset], List[FunctionDef]]:
        """
        Wykonuje pełną analizę pliku PHP.
        
        Args:
            content: Zawartość pliku
            file_path: Ścieżka pliku
            
        Returns:
            Tuple (dependencies, hooks, assets, functions)
        """
        # Reset hooked functions tracker
        self._hooked_functions.clear()
        
        # Find all elements
        hooks = self.find_hooks(content, file_path)
        dependencies = self.find_requires(content, file_path)
        assets = self.find_enqueues(content, file_path)
        functions = self.find_functions(content, file_path)
        
        return dependencies, hooks, assets, functions