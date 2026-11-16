#!/usr/bin/env python3
"""Audit pointer/index implementations for hash and mapping drift.

This is intentionally read-only. It identifies competing pointer/index layers so
recovery can converge them without deleting historical implementations.
"""
from __future__ import annotations

import argparse
import ast
from pathlib import Path

TARGETS = (
    "archwiz/pointer_index.py",
    "archwiz/mapping_pointer_index.py",
    "cli-synthegration/pointer_sync.py",
    "cli-synthegration/synthegration_index.py",
    "cli-synthegration/workspace/compression_sandbox/synthegration_index.py",
    "cli-synthegration/workspace/compression_sandbox/synthegration_index_ref.py",
    "workspace/llm_map/generate_final.py",
    "workspace/llm_map/finalize.py",
)


def inspect(path: Path) -> dict:
    result = {"path": str(path), "exists": path.exists()}
    if not path.exists():
        return result
    text = path.read_text(encoding="utf-8", errors="replace")
    result["sha256_length_mentions"] = {
        "16": text.count("hexdigest()[:16]"),
        "64": text.count("hexdigest()"),
    }
    result["pointer_terms"] = [term for term in ("Pointer", "content_hash", "to_wire", "mapping", "taxonomy") if term in text]
    try:
        tree = ast.parse(text)
        result["classes"] = [n.name for n in tree.body if isinstance(n, ast.ClassDef)]
        result["functions"] = [n.name for n in tree.body if isinstance(n, ast.FunctionDef)]
    except SyntaxError as exc:
        result["syntax_error"] = str(exc)
    return result


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args()
    root = Path(args.root)
    print("Linguist INDEX alignment audit")
    for relative in TARGETS:
        item = inspect(root / relative)
        print(item)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
