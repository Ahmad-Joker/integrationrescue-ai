"""Filesystem locations. All runtime state lives under VAR_DIR (gitignored)."""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"


def var_dir() -> Path:
    """Runtime state directory; override with IR_VAR_DIR (tests use a temp dir)."""
    path = Path(os.environ.get("IR_VAR_DIR", PROJECT_ROOT / "var")).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def runs_dir() -> Path:
    path = var_dir() / "runs"
    path.mkdir(parents=True, exist_ok=True)
    return path
