"""
Path validation utilities adapted from UFO for safe local save paths.
"""

from __future__ import annotations

import os
import platform
from pathlib import Path
from typing import Optional

_SENSITIVE_DIRS_WINDOWS = [
    "C:\\Windows",
    "C:\\Program Files",
    "C:\\Program Files (x86)",
    "C:\\ProgramData",
]

_SENSITIVE_DIRS_LINUX = [
    "/bin",
    "/sbin",
    "/usr/bin",
    "/usr/sbin",
    "/etc",
    "/boot",
    "/dev",
    "/proc",
    "/sys",
    "/var/run",
    "/lib",
    "/lib64",
]


def validate_path_within_base(path_str: str, base_directory: str) -> str:
    base = Path(base_directory).resolve()
    resolved = Path(path_str).resolve() if Path(path_str).is_absolute() else (base / path_str).resolve()
    if not (str(resolved).startswith(str(base) + os.sep) or resolved == base):
        raise ValueError(
            f"Path '{path_str}' resolves outside the allowed base directory '{base}'"
        )
    return str(resolved)


def validate_path_not_sensitive(path_str: str) -> str:
    resolved = Path(path_str).resolve()
    resolved_str = str(resolved)
    sensitive_dirs = (
        _SENSITIVE_DIRS_WINDOWS if platform.system() == "Windows" else _SENSITIVE_DIRS_LINUX
    )
    for sensitive_dir in sensitive_dirs:
        sensitive_resolved = str(Path(sensitive_dir).resolve())
        if resolved_str.lower().startswith(sensitive_resolved.lower()):
            raise ValueError(
                f"Path '{path_str}' targets a sensitive system directory: {sensitive_dir}"
            )
    return str(resolved)


def validate_save_path(file_dir: str, document_dir: Optional[str] = None) -> str:
    if not file_dir:
        if document_dir:
            return str(Path(document_dir).resolve())
        return os.getcwd()

    resolved = Path(file_dir).resolve()
    if ".." in Path(file_dir).parts:
        raise ValueError(f"Path '{file_dir}' contains directory traversal sequences")
    validate_path_not_sensitive(str(resolved))
    return str(resolved)
