"""Estimate spoken length of a demo/pitch script: counts the quoted narration in its markdown tables.

    python scripts/script_timing.py competition/DEMO_SCRIPT_2_MIN.md competition/PITCH_SCRIPT_6_MIN.md

Narration is any text inside double quotes in a table row's last cell. Reports words and duration at 130/140/150 wpm.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

QUOTED = re.compile(r'"([^"]+)"')


def narration(path: Path) -> list[tuple[str, int]]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---"):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 2 or not re.match(r"^\d+:\d\d", cells[0]):
            continue
        words = sum(len(q.split()) for q in QUOTED.findall(cells[-1]))
        rows.append((cells[0], words))
    return rows


def main() -> None:
    for name in sys.argv[1:]:
        rows = narration(Path(name))
        total = sum(w for _, w in rows)
        print(f"{name}: {total} words in {len(rows)} segments")
        for wpm in (130, 140, 150):
            secs = total / wpm * 60
            print(f"  at {wpm} wpm: {int(secs // 60)}:{int(secs % 60):02d}")
        for seg, words in rows:
            print(f"    {seg:<12} {words:>4} words")


if __name__ == "__main__":
    main()
