#!/usr/bin/env python3
"""Rebuild docs/DEBATE/TOC.md from MATRIX.yaml (single source of tags)."""
from __future__ import annotations
import datetime as dt
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("FAIL: pip install pyyaml", file=sys.stderr)
    sys.exit(2)

ROOT = Path(__file__).resolve().parents[2]
MATRIX = ROOT / "docs" / "DEBATE" / "MATRIX.yaml"
TOC = ROOT / "docs" / "DEBATE" / "TOC.md"


def main() -> int:
    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    debates = data.get("debates") or []
    stale_after = int(data.get("stale_after_days") or 14)
    today = dt.date.today()

    rows = []
    attention = []
    for d in debates:
        last = d.get("last_activity") or d.get("opened") or today.isoformat()
        try:
            last_d = dt.date.fromisoformat(str(last)[:10])
        except ValueError:
            last_d = today
        age = (today - last_d).days
        stale = age >= stale_after and d.get("status") == "open"
        blocker = bool(d.get("blocker"))
        if stale:
            attention.append(("stale", d["id"], f"{age}d since {last}"))
        if blocker:
            attention.append(("blocker", d["id"], d.get("blocker_note") or "flagged"))
        tags = ",".join(d.get("tags") or [])
        path = f"active/{d['id']}/" if d.get("status") != "resolved" else f"resolved/{d['id']}/"
        rows.append(
            f"| {d['id']} | {d.get('title','')} | {d.get('status')} | "
            f"{'yes' if stale else 'no'} | {'yes' if blocker else 'no'} | {tags} | [{path}]({path}) |"
        )

    att_rows = (
        "\n".join(f"| {k} | {i} | {n} |" for k, i, n in attention)
        if attention
        else "| _(none)_ | | |"
    )

    body = f"""# DEBATE — Table of Contents

> **LLM rule:** Prefer this file over any `active/*` body.
> Auto-built {today.isoformat()} from MATRIX.yaml via `scripts/debate/build_toc.py`.

| ID | Title | Status | Stale? | Blocker? | Tags | Path |
|----|-------|--------|--------|----------|------|------|
{chr(10).join(rows) if rows else "| _(none)_ | | | | | | |"}

## Needs attention

| Kind | ID | Note |
|------|-----|------|
{att_rows}

## How to open a debate

```bash
cp docs/DEBATE/_template/TOPIC.md docs/DEBATE/active/<id>/TOPIC.md
# edit MATRIX.yaml + TOPIC.md
python3 scripts/debate/build_toc.py
```

## How to resolve

1. Binding VOTE + MANIFEST Review log (CONSENSUS).
2. Move `active/<id>` → `resolved/<id>`.
3. MATRIX status → `resolved`; rebuild TOC.
"""
    TOC.write_text(body, encoding="utf-8")
    print(f"OK: TOC rebuilt ({len(debates)} debates, {len(attention)} attention flags)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
