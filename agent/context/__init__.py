"""
agent.context package: project info and smart context (task-type-aware context).
"""

from .project_info import (
    get_full_context,
    get_minimal_context,
    PROJECT_INFO,
    CODING_CONVENTIONS,
    CODING_CONVENTIONS_CSS_ONLY,
    CODING_CONVENTIONS_PHP_ONLY,
    WORDPRESS_TIPS,
    DIRECTORY_STRUCTURE,
    BRANDING,
    CRITICAL_FILES,
    TASK_FILE_MAPPING,
)
from .smart_context import (
    classify_task_type,
    get_file_map,
    get_context_for_task,
)

__all__ = [
    "get_full_context",
    "get_minimal_context",
    "PROJECT_INFO",
    "CODING_CONVENTIONS",
    "CODING_CONVENTIONS_CSS_ONLY",
    "CODING_CONVENTIONS_PHP_ONLY",
    "WORDPRESS_TIPS",
    "DIRECTORY_STRUCTURE",
    "BRANDING",
    "CRITICAL_FILES",
    "TASK_FILE_MAPPING",
    "classify_task_type",
    "get_file_map",
    "get_context_for_task",
]
