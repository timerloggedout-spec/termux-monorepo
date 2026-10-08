"""Detect keep-alive version drift. Does not rewrite VERSION."""
from __future__ import annotations

from pathlib import Path

def package_version(pipelines_dir: Path) -> str:
    return (pipelines_dir / "VERSION").read_text(encoding="utf-8").strip()

def mismatch(init_version: str, file_version: str) -> bool:
    return str(init_version).strip() != str(file_version).strip()
