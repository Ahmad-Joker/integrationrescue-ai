"""Filesystem locations. All runtime state lives under VAR_DIR (gitignored)."""

from __future__ import annotations

import os
from pathlib import Path

PACKAGE_DIR = Path(__file__).resolve().parent
BACKEND_DIR = PACKAGE_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent
TEMPLATES_DIR = PACKAGE_DIR / "templates"


def load_env_file(path: Path | None = None) -> list[str]:
    """Load ``KEY=VALUE`` lines from the repo's ``.env`` into os.environ; real environment variables win.

    Kept dependency-free on purpose. Returns the names set (never values, so callers can log them safely).
    Child processes never inherit these: the sync service and sandbox pass an allow-listed environment.
    """
    path = path or PROJECT_ROOT / ".env"
    if os.environ.get("IR_SKIP_DOTENV") or not path.is_file():
        return []
    loaded = []
    for line in path.read_text(encoding="utf-8-sig").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.removeprefix("export ").partition("=")
        key, value = key.strip(), value.split(" #", 1)[0].strip().strip("'\"")
        if key and value and key not in os.environ:
            os.environ[key] = value
            loaded.append(key)
    return loaded


def var_dir() -> Path:
    """Runtime state directory; override with IR_VAR_DIR (tests use a temp dir)."""
    path = Path(os.environ.get("IR_VAR_DIR", PROJECT_ROOT / "var")).resolve()
    path.mkdir(parents=True, exist_ok=True)
    return path


def runs_dir() -> Path:
    path = var_dir() / "runs"
    path.mkdir(parents=True, exist_ok=True)
    return path
