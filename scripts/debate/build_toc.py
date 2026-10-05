#!/usr/bin/env python3
"""Rebuild docs/DEBATE/TOC.md from MATRIX.yaml (single source of tags).

The header stamp is not wall-clock. CI sets DEBATE_TOC_DATE to the MATRIX.yaml
commit date so a Monday schedule does not fail on date-only drift (run
37377726547). Stale/blocker age still uses today unless DEBATE_TOC_DATE is set,
in which case both stamp and age share that pin.
"""
from __future__ import annotations
import datetime as dt
import os
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


def pinned_date() -> dt.date | None:
    raw = (os.environ.get("DEBATE_TOC_DATE") or "").strip()
    if not raw:
        return None
    if raw.isdigit():
        return dt.datetime.fromtimestamp(int(raw), dt.timezone.utc).date()
    try:
        return dt.date.fromisoformat(raw[:10])
    except ValueError:
        print(f"FAIL: DEBATE_TOC_DATE not a date: {raw}", file=sys.stderr)
        sys.exit(2)


def main() -> int:
    data = yaml.safe_load(MATRIX.read_text(encoding="utf-8"))
    debates = data.get("debates") or []
    stale_after = int(data.get("stale_after_days") or 14)
    pin = pinned_date()
    today = pin or dt.date.today()
    stamp = pin.isoformat() if pin else "MATRIX.yaml"

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
    stamp_line = (
        f"> Auto-built {stamp} from MATRIX.yaml via `scripts/debate/build_toc.py`."
        if pin
        else "> Auto-built from MATRIX.yaml via `scripts/debate/build_toc.py` (no wall-clock stamp)."
    )

    body = f"""# DEBATE — Table of Contents

> **LLM rule:** Prefer this file over any `active/*` body.
{stamp_line}

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
    print(f"OK: TOC rebuilt ({len(debates)} debates, {len(attention)} attention flags, stamp={stamp})")
    return 0


if __name__ == "__main__":
    sys.exit(main())
