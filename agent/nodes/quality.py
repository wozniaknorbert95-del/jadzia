"""
Quality assurance validation for code changes.
Validates PHP syntax, CSS syntax, and WordPress safety before deployment.
"""

import re
from typing import Dict, List, Any

from agent.log import log_event, EventType


async def validate_changes(diffs: Dict[str, Any], ssh_orch: Any) -> Dict[str, Any]:
    """
    Validates all pending file changes before deployment.

    Args:
        diffs: Dictionary of {filepath: {"old": str, "new": str}} or {filepath: diff_str}.
               Code uses .get("new", "") so pass {"new": content} per file when diff is string.
        ssh_orch: SSHOrchestrator instance for PHP validation

    Returns:
        {
            "valid": bool,
            "errors": dict,      # {filename: [error_messages]}
            "warnings": dict,   # {filename: [warning_messages]}
            "details": dict     # {filename: validation_result}
        }
    """
    errors: Dict[str, List[str]] = {}
    warnings: Dict[str, List[str]] = {}
    details: Dict[str, Any] = {}

    log_event(EventType.FILE_WRITE, f"[QUALITY] Starting validation for {len(diffs)} files")

    for filepath, diff_data in diffs.items():
        if isinstance(diff_data, dict):
            new_content = diff_data.get("new", "")
        else:
            new_content = str(diff_data) if diff_data else ""
        file_errors: List[str] = []
        file_warnings: List[str] = []

        if filepath.endswith(".php"):
            php_result = await syntax_check_php(new_content, ssh_orch)
            details[filepath] = php_result

            if not php_result["valid"]:
                file_errors.append(f"PHP syntax error: {php_result.get('error', 'unknown')}")

            from agent.guardrails import check_wordpress_safety
            safety_result = check_wordpress_safety(new_content, filepath)

            if not safety_result.get("safe", True):
                file_errors.append(f"Security violation: {safety_result.get('reason', 'unknown')}")

        elif filepath.endswith(".css"):
            css_result = syntax_check_css(new_content)
            details[filepath] = css_result

            if not css_result["valid"]:
                file_errors.extend(css_result["errors"])
            if css_result.get("warnings"):
                file_warnings.extend(css_result["warnings"])

        if file_errors:
            errors[filepath] = file_errors
        if file_warnings:
            warnings[filepath] = file_warnings

    is_valid = len(errors) == 0

    log_event(
        EventType.FILE_WRITE,
        f"[QUALITY] Validation {'PASSED' if is_valid else 'FAILED'}: "
        f"{len(errors)} errors, {len(warnings)} warnings",
    )

    return {
        "valid": is_valid,
        "errors": errors,
        "warnings": warnings,
        "details": details,
    }


async def syntax_check_php(content: str, ssh_orch: Any) -> Dict[str, Any]:
    """
    Validates PHP syntax using server's PHP interpreter via SSH.

    Args:
        content: PHP file content to validate
        ssh_orch: SSHOrchestrator instance

    Returns:
        {"valid": bool, "error": str|None, "line": int|None}
    """
    try:
        escaped_content = content.replace("'", "'\"'\"'")
        command = f"printf '%s' '{escaped_content}' | php -l 2>&1"
        result = await ssh_orch.run_command(command, timeout=15)
        output = (result.get("stdout", "") or "") + (result.get("stderr", "") or "")

        if "No syntax errors" in output:
            return {"valid": True, "error": None, "line": None}

        line_match = re.search(r"on line (\d+)", output)
        line_num = int(line_match.group(1)) if line_match else None
        error_match = re.search(r"Parse error:\s+(.+?)\s+in -", output, re.DOTALL)
        error_msg = error_match.group(1).strip() if error_match else output.strip()

        return {
            "valid": False,
            "error": error_msg,
            "line": line_num,
        }
    except Exception as e:
        log_event(EventType.FILE_WRITE, f"[QUALITY] PHP validation exception: {str(e)}")
        return {
            "valid": False,
            "error": f"Validation failed: {str(e)}",
            "line": None,
        }


def syntax_check_css(content: str) -> Dict[str, Any]:
    """
    Validates CSS syntax using regex patterns.

    Checks balanced braces {}, balanced parentheses in values,
    and optional warnings for orphaned semicolons and empty rules.

    Args:
        content: CSS file content

    Returns:
        {"valid": bool, "errors": List[str], "warnings": List[str]}
    """
    errors: List[str] = []
    warnings: List[str] = []

    content_no_comments = re.sub(r"/\*.*?\*/", "", content, flags=re.DOTALL)

    open_braces = content_no_comments.count("{")
    close_braces = content_no_comments.count("}")
    if open_braces != close_braces:
        errors.append(f"Unbalanced braces: {open_braces} opening, {close_braces} closing")

    open_parens = content_no_comments.count("(")
    close_parens = content_no_comments.count(")")
    if open_parens != close_parens:
        errors.append(
            f"Unbalanced parentheses: {open_parens} opening, {close_parens} closing"
        )

    rules = re.split(r"\{[^}]*\}", content_no_comments)
    for i, between_rules in enumerate(rules):
        between_rules = between_rules.strip()
        if between_rules and ";" in between_rules:
            if not re.match(r"^\s*@(import|charset|font-face)", between_rules):
                warnings.append(f"Unexpected semicolon outside rule block (section {i + 1})")

    if re.search(r":\s*;", content_no_comments):
        warnings.append("Empty CSS property value detected (property: ;)")

    if re.search(r"\{\s*\}", content_no_comments):
        warnings.append("Empty CSS rule block detected")

    return {
        "valid": len(errors) == 0,
        "errors": errors,
        "warnings": warnings,
    }
