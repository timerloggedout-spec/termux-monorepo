#!/usr/bin/env python3
"""Build a read-only, provenance-bearing static architecture portal bundle."""
from __future__ import annotations

import argparse
import hashlib
import html as html_lib
import json
import os
import re
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_VERSION = 1
SELECTED_OPERATIONS_DOCS = (
    "docs/ops/SHE-DASHBOARD-INDEX.md",
    "docs/ops/SHE-DASHBOARD-PRD.md",
    "docs/ops/SHE-DASHBOARD-UI-UX-CONTROL-PLANE.md",
    "docs/ops/SHE-DASHBOARD-SNAPSHOT-CONTRACT.md",
    "docs/ops/SHE-INTEGRATION-FINDINGS.md",
    "docs/ops/INTEGRATION-GRAPH-MATRIX.md",
    "docs/ops/DEPLOYMENT-LANES.md",
    "docs/ops/SITE-MAP.md",
    "docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd",
)


def _safe_repo_path(path: Path, root: Path) -> str:
    """Return a repository-relative path and reject symlinks outside root."""
    resolved_root = root.resolve()
    resolved_path = path.resolve(strict=True)
    try:
        return resolved_path.relative_to(resolved_root).as_posix()
    except ValueError as exc:
        raise ValueError(f"source escapes repository root: {path}") from exc


def discover_sources(root: Path = ROOT) -> list[Path]:
    """Discover the bounded architecture documentation and visual-asset estate."""
    candidates: set[Path] = set()
    fixed = [root / "architecture.md"]
    fixed.extend(root / name for name in SELECTED_OPERATIONS_DOCS)
    candidates.update(path for path in fixed if path.is_file())

    docs_root = root / "docs"
    if docs_root.is_dir():
        candidates.update(
            path for path in docs_root.rglob("*")
            if path.is_file() and path.suffix.lower() in {".mmd", ".svg"}
        )
    scan_rules = (
        (root / "docs/architecture", {".md"}),
        (root / "docs/ops/generated", {".png"}),
    )
    for directory, suffixes in scan_rules:
        if directory.is_dir():
            candidates.update(
                path for path in directory.rglob("*")
                if path.is_file() and path.suffix.lower() in suffixes
            )
    return sorted(candidates, key=lambda path: _safe_repo_path(path, root).casefold())


def _kind(path: Path) -> str:
    return {
        ".md": "document",
        ".mmd": "mermaid",
        ".svg": "svg",
        ".png": "png",
    }[path.suffix.lower()]


def _category(relative: str) -> str:
    if relative == "architecture.md":
        return "Architecture / Overview"
    if relative.startswith("docs/architecture/flows/"):
        return "Architecture / Flow Modules"
    if relative.startswith("docs/architecture/"):
        return "Architecture / Reference"
    if relative.startswith("docs/agentic/"):
        return "Architecture / Agentic"
    if relative.startswith("docs/assets/"):
        return "Architecture / Imported Assets"
    if relative.startswith("docs/graph/"):
        return "Architecture / Graph"
    if relative.startswith("docs/ops/diagrams/"):
        return "Operations / Mermaid Library"
    if relative.startswith("docs/ops/generated/"):
        return "Operations / Generated Assets"
    if relative.startswith("docs/ops/"):
        return "Operations / SHE and Contracts"
    return "Architecture / Other"


def _plain_summary(text: str) -> str:
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    for line in lines:
        if line.startswith(("#", "```", "---", "|")):
            continue
        line = re.sub(r"[\x60*_>\[\]()]","", line)
        line = re.sub(r"\s+", " ", line).strip()
        if line:
            return line[:240]
    return "Canonical repository architecture source."


def _mermaid_input(text: str) -> str:
    """Extract a fenced Mermaid block when a .mmd file also contains Markdown."""
    match = re.search(r"```mermaid[ \\t]*\\r?\\n(.*?)```", text, flags=re.IGNORECASE | re.DOTALL)
    if match:
        return match.group(1).strip() + "\\n"
    return text if text.endswith("\\n") else text + "\\n"


def _title(path: Path, text: str) -> str:
    if path.suffix.lower() == ".svg":
        match = re.search(r"<title[^>]*>(.*?)</title>", text, flags=re.IGNORECASE | re.DOTALL)
        if match:
            title = html_lib.unescape(re.sub(r"<[^>]+>", "", match.group(1))).strip()
            if title:
                return title
    for line in text.splitlines()[:30]:
        match = re.match(r"^#\s+(.+?)\s*#*$", line.strip())
        if match:
            return match.group(1).strip()
    return path.stem.replace("-", " ").replace("_", " ").title()


def _reset_generated_dirs(output: Path) -> None:
    for name in ("source", "render-inputs", "assets/imported", "assets/previews", "assets/diagrams"):
        target = output / name
        if target.exists():
            shutil.rmtree(target)
        target.mkdir(parents=True, exist_ok=True)


def build_portal(
    root: Path = ROOT,
    output: Path | None = None,
    source_ref: str = "master",
    source_sha: str = "unknown",
) -> dict[str, object]:
    """Copy canonical sources and write a catalog with hashes and build identity."""
    root = root.resolve()
    output = (output or (root / "_site/architecture")).resolve()
    if output == root or (root / "docs") in output.parents or output == root / "docs":
        raise ValueError("output must be a dedicated site directory outside the documentation source tree")
    output.mkdir(parents=True, exist_ok=True)
    _reset_generated_dirs(output)

    items: list[dict[str, object]] = []
    for source in discover_sources(root):
        relative = _safe_repo_path(source, root)
        data = source.read_bytes()
        kind = _kind(source)
        text = data.decode("utf-8", errors="replace") if kind in {"document", "mermaid", "svg"} else ""
        record: dict[str, object] = {
            "id": relative,
            "path": relative,
            "kind": kind,
            "title": _title(source, text) if text else source.stem.replace("-", " ").title(),
            "summary": (
                _plain_summary(text) if kind == "document" else
                "Editable Mermaid diagram source." if kind == "mermaid" else
                "Imported SVG vector asset." if kind == "svg" else
                "Generated visual preview."
            ),
            "category": _category(relative),
            "bytes": len(data),
            "sha256": hashlib.sha256(data).hexdigest(),
            "source_ref": source_ref,
            "source_url": f"https://github.com/timerloggedout-spec/termux-monorepo/blob/{source_ref}/{relative}",
            "raw_url": f"https://raw.githubusercontent.com/timerloggedout-spec/termux-monorepo/{source_ref}/{relative}",
        }

        if kind in {"document", "mermaid"}:
            site_path = f"source/{relative}"
            destination = output / site_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            record["site_path"] = site_path
            if kind == "mermaid":
                render_input_path = f"render-inputs/{relative}"
                render_input = output / render_input_path
                render_input.parent.mkdir(parents=True, exist_ok=True)
                render_input.write_text(_mermaid_input(text), encoding="utf-8")
                record["render_input_path"] = render_input_path
                record["render_path"] = f"assets/diagrams/{relative[:-4]}.svg"
        elif kind == "svg":
            asset_path = f"assets/imported/{relative}"
            destination = output / asset_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            record["asset_path"] = asset_path
        elif kind == "png":
            asset_path = f"assets/previews/{relative}"
            destination = output / asset_path
            destination.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source, destination)
            record["asset_path"] = asset_path
        items.append(record)

    if not items:
        raise ValueError("architecture source inventory is empty")

    catalog: dict[str, object] = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_ref": source_ref,
        "source_sha": source_sha,
        "source_root": "architecture.md + docs/architecture Markdown + docs/**/*.mmd + docs/**/*.svg + selected SHE docs + generated PNG",
        "item_count": len(items),
        "document_count": sum(item["kind"] == "document" for item in items),
        "diagram_count": sum(item["kind"] == "mermaid" for item in items),
        "svg_count": sum(item["kind"] == "svg" for item in items),
        "items": items,
    }
    (output / "catalog.json").write_text(
        json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return catalog


def verify_rendered(output: Path) -> list[str]:
    """Return Mermaid render paths that are missing or empty in a built bundle."""
    catalog_path = output / "catalog.json"
    if not catalog_path.is_file():
        return ["catalog.json"]
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    missing: list[str] = []
    for item in catalog.get("items", []):
        if item.get("kind") != "mermaid":
            continue
        relative = item.get("render_path", "")
        if not relative or Path(relative).is_absolute() or ".." in Path(relative).parts:
            missing.append(str(relative or item.get("path", "unknown")))
            continue
        target = output / relative
        if not target.is_file() or target.stat().st_size == 0:
            missing.append(relative)
            continue
        if b"<svg" not in target.read_bytes()[:4096]:
            missing.append(relative)
    return missing


def finalize_bundle(output: Path) -> None:
    """Remove build-only render inputs and their private catalog pointers."""
    catalog_path = output / "catalog.json"
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    for item in catalog.get("items", []):
        item.pop("render_input_path", None)
    catalog_path.write_text(
        json.dumps(catalog, indent=2, sort_keys=True, ensure_ascii=False) + "\\n",
        encoding="utf-8",
    )
    shutil.rmtree(output / "render-inputs", ignore_errors=True)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path, default=ROOT / "_site/architecture")
    parser.add_argument("--source-ref", default=os.environ.get("GITHUB_REF_NAME", "master"))
    parser.add_argument("--source-sha", default=os.environ.get("GITHUB_SHA", "unknown"))
    parser.add_argument("--verify-rendered", action="store_true")
    parser.add_argument("--finalize", action="store_true", help="remove build-only render inputs after successful SVG verification")
    args = parser.parse_args(argv)

    if args.verify_rendered:
        missing = verify_rendered(args.output)
        if missing:
            print("Architecture Explorer SVG render verification: FAIL", file=sys.stderr)
            for path in missing:
                print(f" - missing or invalid: {path}", file=sys.stderr)
            return 1
        print("Architecture Explorer SVG render verification: PASS")
        if args.finalize:
            finalize_bundle(args.output)
            print("Architecture Explorer bundle finalized")
        return 0

    catalog = build_portal(args.root, args.output, args.source_ref, args.source_sha)
    print(
        "Architecture Explorer bundle: "
        f"{catalog['item_count']} items; {catalog['document_count']} Markdown; "
        f"{catalog['diagram_count']} Mermaid; {catalog['svg_count']} imported SVG; "
        f"source {catalog['source_sha']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
