"""Run the competition demo locally exactly as the container runs it: one process serving API + built dashboard.

    npm run build --prefix frontend
    .venv/Scripts/python scripts/serve_demo.py            # http://127.0.0.1:8080

Uses IR_ACCESS_TOKEN / IR_ADMIN_TOKEN from the environment or .env; when absent it generates throwaway codes for this
local run and prints them once (they are never written to disk). State goes to var/demo (fictional, git-ignored).
"""

from __future__ import annotations

import os
import secrets
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "backend"))

from integrationrescue.paths import load_env_file  # noqa: E402


def main() -> None:
    load_env_file()
    dist = ROOT / "frontend" / "dist"
    if not (dist / "index.html").is_file():
        sys.exit("frontend/dist is missing: run `npm run build --prefix frontend` first")
    os.environ.setdefault("IR_DEMO_MODE", "1")
    os.environ.setdefault("IR_STATIC_DIR", str(dist))
    os.environ.setdefault("IR_VAR_DIR", str(ROOT / "var" / "demo"))
    for name in ("IR_ACCESS_TOKEN", "IR_ADMIN_TOKEN"):
        if not os.environ.get(name):
            os.environ[name] = secrets.token_urlsafe(18)
            print(f"{name} for this local run: {os.environ[name]}")
    port = int(os.environ.get("PORT", "8080"))
    import uvicorn  # noqa: PLC0415 - imported after the environment is final

    uvicorn.run("integrationrescue.api:app", host="127.0.0.1", port=port, app_dir=str(ROOT / "backend"))


if __name__ == "__main__":
    main()
