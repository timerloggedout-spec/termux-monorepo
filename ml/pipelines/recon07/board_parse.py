"""Parse the generated lane-matrix markdown table. Writer-only input."""
from __future__ import annotations

import re
from pathlib import Path

from ml.pipelines.lanes.vocab import VALID_LANES

ROW_RE = re.compile(
    r"^\|\s*#(\d+)\s*\|\s*([0-9.]+)\s*\|\s*(EXTRACT|CANDIDATE|NEED_EVIDENCE|SUPERSEDE)\s*\|\s*([^|]*)\|"
)


def parse_board(text: str) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for line in text.splitlines():
        match = ROW_RE.match(line.strip())
        if not match:
            continue
        lane = match.group(3)
        if lane not in VALID_LANES:
            raise ValueError(lane)
        reasons = tuple(part.strip() for part in match.group(4).split(",") if part.strip())
        rows.append(
            {
                "number": int(match.group(1)),
                "age_days": float(match.group(2)),
                "lane": lane,
                "reasons": reasons,
            }
        )
    return rows


def default_board_path(root: Path | None = None) -> Path:
    base = root or Path(__file__).resolve().parents[3]
    return base / "docs" / "ops" / "generated" / "lane-matrix-status.md"


def load_board(path: Path | None = None) -> list[dict[str, object]]:
    target = path or default_board_path()
    return parse_board(target.read_text(encoding="utf-8"))
