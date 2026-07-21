"""Safe tar extraction utilities for downloaded SSH archives."""

from __future__ import annotations

import tarfile
from pathlib import Path


class UnsafeArchiveError(ValueError):
    """Raised when a tar member escapes the extraction directory."""


def safe_extractall(archive: tarfile.TarFile, destination: Path) -> None:
    """Extract regular files only when every resolved member stays in destination."""
    root = destination.resolve()
    members = archive.getmembers()
    for member in members:
        target = (root / member.name).resolve()
        if not target.is_relative_to(root):
            raise UnsafeArchiveError(f"Archive member escapes destination: {member.name}")
        if member.issym() or member.islnk() or member.isdev():
            raise UnsafeArchiveError(f"Archive member type is forbidden: {member.name}")
    archive.extractall(root, members=members)
