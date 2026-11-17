"""Check that relative links in the repository's Markdown files point to files that exist.

    python scripts/check_links.py

External (http) links are not fetched. Exit code 1 lists every broken link.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LINK = re.compile(r"\[[^\]]*\]\(([^)\s]+)\)")
SKIP_DIRS = {"node_modules", ".venv", "var", ".git", "dist", "test-results"}


def main() -> int:
    broken = []
    files = [p for p in ROOT.rglob("*.md") if not SKIP_DIRS & set(p.relative_to(ROOT).parts)]
    for md in files:
        for target in LINK.findall(md.read_text(encoding="utf-8")):
            if target.startswith(("http://", "https://", "mailto:", "#")):
                continue
            path = target.split("#", 1)[0].split(":", 1)[0] if not re.match(r"^[A-Za-z]:", target) else target
            if not path:
                continue
            if not (md.parent / path).exists():
                broken.append(f"{md.relative_to(ROOT)} -> {target}")
    print(f"checked {len(files)} Markdown files")
    for b in broken:
        print("BROKEN", b)
    return 1 if broken else 0


if __name__ == "__main__":
    sys.exit(main())
