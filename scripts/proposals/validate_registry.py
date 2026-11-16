#!/usr/bin/env python3
"""Validate docs/proposals/registry.yaml against on-disk active/ closed/ layout."""
from __future__ import annotations
import sys
from pathlib import Path
try:
    import yaml
except ImportError:
    yaml = None
ROOT = Path(__file__).resolve().parents[2]
REG = ROOT / "docs" / "proposals" / "registry.yaml"
ACTIVE = ROOT / "docs" / "proposals" / "active"
REQUIRED_STATES = {"draft", "posted", "in_review", "accepted", "executing", "blocked", "closed"}

def load_registry():
    if not REG.exists():
        print(f"FAIL: missing {REG}", file=sys.stderr)
        sys.exit(2)
    text = REG.read_text(encoding="utf-8")
    if yaml is not None:
        data = yaml.safe_load(text)
    else:
        if "proposals:" not in text:
            print("FAIL: no proposals: key", file=sys.stderr)
            sys.exit(2)
        print("WARN: PyYAML not installed; structural checks only")
        return {"_raw": text}
    if not isinstance(data, dict) or "proposals" not in data:
        print("FAIL: registry missing proposals list", file=sys.stderr)
        sys.exit(2)
    return data

def main() -> int:
    data = load_registry()
    errors = []
    if "_raw" in data:
        for pdir in sorted(ACTIVE.glob("*")) if ACTIVE.exists() else []:
            if not (pdir / "MANIFEST.md").exists():
                errors.append(f"active/{pdir.name}: missing MANIFEST.md")
        if errors:
            for e in errors:
                print(f"FAIL: {e}", file=sys.stderr)
            return 1
        print("OK (weak): registry present; active manifests exist")
        return 0
    proposals = data.get("proposals") or []
    seen_ids = set()
    for p in proposals:
        pid = p.get("id")
        if not pid:
            errors.append("proposal missing id")
            continue
        if pid in seen_ids:
            errors.append(f"duplicate id: {pid}")
        seen_ids.add(pid)
        status = p.get("status", "")
        if status not in REQUIRED_STATES:
            errors.append(f"{pid}: invalid status {status!r}")
        path = p.get("path") or f"active/{pid}/"
        full = ROOT / "docs" / "proposals" / path
        if status != "closed" and not full.exists():
            errors.append(f"{pid}: path missing on disk: {path}")
        elif status != "closed":
            if not (full / "MANIFEST.md").exists():
                errors.append(f"{pid}: missing MANIFEST.md under {path}")
            if not (full / "ITEMS.md").exists():
                errors.append(f"{pid}: missing ITEMS.md under {path}")
    if ACTIVE.exists():
        for pdir in ACTIVE.iterdir():
            if pdir.is_dir() and pdir.name not in seen_ids:
                errors.append(f"orphan active dir (not in registry): {pdir.name}")
    if errors:
        for e in errors:
            print(f"FAIL: {e}", file=sys.stderr)
        return 1
    print(f"OK: {len(seen_ids)} proposals consistent with disk")
    return 0

if __name__ == "__main__":
    sys.exit(main())
