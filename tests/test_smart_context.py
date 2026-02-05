"""
Tests for Smart Context (FAZA 3): classify_task_type, get_file_map, get_context_for_task.
"""

import pytest
from unittest.mock import patch

from agent.context.smart_context import (
    classify_task_type,
    get_file_map,
    get_context_for_task,
)


# ---- classify_task_type ----

def test_classify_task_type_css_only():
    """'zmień kolor' / 'css' / 'style' -> css_only"""
    assert classify_task_type("zmień kolor przycisku") == "css_only"
    assert classify_task_type("zmien kolor tla") == "css_only"
    assert classify_task_type("dodaj css do nagłówka") == "css_only"
    assert classify_task_type("style dla przycisku") == "css_only"
    assert classify_task_type("zmień font") == "css_only"


def test_classify_task_type_php_only():
    """'funkcja' / 'hook' / 'filter' / 'functions.php' -> php_only"""
    assert classify_task_type("dodaj funkcję do theme") == "php_only"
    assert classify_task_type("hook woocommerce") == "php_only"
    assert classify_task_type("add_filter do ceny") == "php_only"
    assert classify_task_type("edytuj functions.php") == "php_only"
    assert classify_task_type("wp-content/themes/child/functions.php") == "php_only"


def test_classify_task_type_template():
    """'szablon' / 'template' -> template"""
    assert classify_task_type("zmień szablon produktu") == "template"
    assert classify_task_type("template part header") == "template"


def test_classify_task_type_full():
    """Reszta -> full"""
    assert classify_task_type("zrób coś ogólnego") == "full"
    assert classify_task_type("sprawdź sklep") == "full"
    assert classify_task_type("") == "full"


# ---- get_file_map ----

def test_get_file_map_returns_list_without_content():
    """get_file_map zwraca listę dictów z path, size, role; bez treści plików."""
    with patch("agent.tools.list_files") as mock_list:
        mock_list.side_effect = [
            ["style.css", "theme.css"],
            ["functions.php", "inc/helper.php"],
        ]
        result = get_file_map("")
    assert isinstance(result, list)
    for entry in result:
        assert "path" in entry
        assert "size" in entry
        assert "role" in entry
        assert "content" not in entry
    paths = [e["path"] for e in result]
    assert "style.css" in paths
    assert "functions.php" in paths


def test_get_file_map_assigns_roles():
    """role: .css -> style, functions.php -> functions, *.php -> template."""
    with patch("agent.tools.list_files") as mock_list:
        mock_list.side_effect = [
            ["style.css"],
            ["functions.php", "woocommerce/single-product.php"],
        ]
        result = get_file_map("")
    roles = {e["path"]: e["role"] for e in result}
    assert roles.get("style.css") == "style"
    assert roles.get("functions.php") == "functions"
    assert roles.get("woocommerce/single-product.php") == "template"


# ---- get_context_for_task ----

def test_get_context_for_task_css_only():
    """css_only: planner_context tylko .css, conventions bez WORDPRESS_TIPS."""
    file_map = [
        {"path": "style.css", "size": 0, "role": "style"},
        {"path": "functions.php", "size": 0, "role": "functions"},
    ]
    ctx = get_context_for_task("css_only", file_map)
    assert "system_prompt" in ctx
    assert "planner_context" in ctx
    assert "conventions" in ctx
    assert "style.css" in ctx["planner_context"]
    assert "functions.php" not in ctx["planner_context"]
    # conventions dla CSS nie powinien zawierać woocommerce hooków (WORDPRESS_TIPS)
    assert "woocommerce_before_main_content" not in ctx["conventions"]
    assert "BEM" in ctx["conventions"] or "kebab-case" in ctx["conventions"]


def test_get_context_for_task_php_only():
    """php_only: planner_context tylko .php, conventions z WORDPRESS_TIPS."""
    file_map = [
        {"path": "style.css", "size": 0, "role": "style"},
        {"path": "functions.php", "size": 0, "role": "functions"},
    ]
    ctx = get_context_for_task("php_only", file_map)
    assert "functions.php" in ctx["planner_context"]
    assert "woocommerce_before_main_content" in ctx["conventions"] or "get_site_url" in ctx["conventions"]


def test_get_context_for_task_full():
    """full: system_prompt pełny, planner_context wszystkie ścieżki."""
    file_map = [
        {"path": "style.css", "size": 0, "role": "style"},
        {"path": "functions.php", "size": 0, "role": "functions"},
    ]
    ctx = get_context_for_task("full", file_map)
    assert "style.css" in ctx["planner_context"]
    assert "functions.php" in ctx["planner_context"]
    assert "WORDPRESS" in ctx["system_prompt"] or "WordPress" in ctx["system_prompt"]


# ---- Token metrics (dokumentacja) ----
# PRZED (pełny kontekst dla "zmień kolor"): ~3000 input tokenów (planer + pełna struktura 50 plików + get_minimal_context).
# PO (smart context css_only): cel ~1000 input tokenów (ok. 60% mniej).
# Pomiar: porównaj [COST] logi przed/po dla jednego wywołania "zmień kolor przycisku" (planer only lub planer+coder).
