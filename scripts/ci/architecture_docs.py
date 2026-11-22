#!/usr/bin/env python3
"""Generate and validate the versioned repository architecture manifest."""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
ARCHITECTURE_DIR = Path("docs/architecture")
VERSION_PATH = ARCHITECTURE_DIR / "VERSION"
CHANGELOG_PATH = ARCHITECTURE_DIR / "CHANGELOG.md"
MANIFEST_PATH = ARCHITECTURE_DIR / "generated/architecture-manifest.json"
FLOW_DIR = ARCHITECTURE_DIR / "flows"
FLOW_RENDER_DIR = ARCHITECTURE_DIR / "generated/flows"
OPS_DIAGRAM_DIR = Path("docs/ops/diagrams")
SHE_DIAGRAM = Path("docs/ops/SHE-DASHBOARD-ARCHITECTURE.mmd")
SCHEMA = "repository-architecture-manifest/v1"
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")


def _read_version(root: Path) -> tuple[str, tuple[int, int, int]]:
    path = root / VERSION_PATH
    if not path.is_file():
        raise ValueError(f"missing architecture version file: {VERSION_PATH.as_posix()}")
    value = path.read_text(encoding="utf-8").strip()
    match = SEMVER.fullmatch(value)
    if not match:
        raise ValueError(
            f"architecture version must use stable semantic version "
            f"MAJOR.MINOR.PATCH: {value!r}"
        )
    return value, tuple(int(part) for part in match.groups())


def _source_paths(root: Path) -> list[Path]:
    required = [
        root / "architecture.md",
        root / VERSION_PATH,
        root / ARCHITECTURE_DIR / "VERSIONING.md",
        root / CHANGELOG_PATH,
        root / ARCHITECTURE_DIR / "README.md",
    ]
    missing = [
        path.relative_to(root).as_posix()
        for path in required
        if not path.is_file()
    ]
    if missing:
        raise ValueError("missing required architecture sources: " + ", ".join(missing))

    paths = set(required)
    for path in (root / ARCHITECTURE_DIR).rglob("*"):
        if path.is_file() and path.suffix.lower() in {".md", ".mmd"}:
            relative = path.relative_to(root).as_posix()
            if not relative.startswith("docs/architecture/generated/"):
                paths.add(path)

    ops_diagrams = root / OPS_DIAGRAM_DIR
    if ops_diagrams.is_dir():
        paths.update(
            path for path in ops_diagrams.glob("*.mmd") if path.is_file()
        )

    she_diagram = root / SHE_DIAGRAM
    if she_diagram.is_file():
        paths.add(she_diagram)

    return sorted(
        paths,
        key=lambda path: path.relative_to(root).as_posix(),
    )


def _flow_diagrams(root: Path) -> list[Path]:
    directory = root / FLOW_DIR
    if not directory.is_dir():
        return []
    return sorted(
        path for path in directory.glob("*.mmd") if path.is_file()
    )


def _validate_flow_pairs(root: Path, diagrams: list[Path]) -> None:
    for source in diagrams:
        mapping = source.with_suffix(".md")
        if not mapping.is_file():
            raise ValueError(
                f"missing paired architecture flow mapping for "
                f"{source.relative_to(root).as_posix()}: "
                f"{mapping.relative_to(root).as_posix()}"
            )


def build_manifest(root: Path = ROOT) -> dict[str, object]:
    version, _ = _read_version(root)
    sources: list[dict[str, str]] = []
    source_set = hashlib.sha256()

    for path in _source_paths(root):
        relative = path.relative_to(root).as_posix()
        content = path.read_bytes()
        digest = hashlib.sha256(content).hexdigest()
        source_set.update(relative.encode("utf-8"))
        source_set.update(b"\0")
        source_set.update(content)
        source_set.update(b"\0")

        is_rendered_diagram = (
            path.parent == root / FLOW_DIR
            or path.parent == root / OPS_DIAGRAM_DIR
        ) and path.suffix.lower() == ".mmd"

        sources.append({
            "path": relative,
            "kind": (
                "diagram-source"
                if is_rendered_diagram
                else "architecture-document"
            ),
            "sha256": digest,
        })

    flow_sources = _flow_diagrams(root)
    _validate_flow_pairs(root, flow_sources)

    diagrams: list[dict[str, str]] = []
    render_pairs = [
        (
            source,
            root / FLOW_RENDER_DIR / f"{source.stem}.svg",
        )
        for source in flow_sources
    ]

    ops_directory = root / OPS_DIAGRAM_DIR
    if ops_directory.is_dir():
        render_pairs.extend(
            (
                source,
                root / "docs/ops/generated" / f"{source.stem}.png",
            )
            for source in sorted(ops_directory.glob("*.mmd"))
            if source.is_file()
        )

    for source, render in render_pairs:
        relative_source = source.relative_to(root).as_posix()
        if not render.is_file():
            raise ValueError(
                f"missing architecture diagram render for {relative_source}: "
                f"{render.relative_to(root).as_posix()}"
            )
        diagrams.append({
            "source": relative_source,
            "source_sha256": hashlib.sha256(
                source.read_bytes()
            ).hexdigest(),
            "render": render.relative_to(root).as_posix(),
            "render_sha256": hashlib.sha256(
                render.read_bytes()
            ).hexdigest(),
        })

    return {
        "schema": SCHEMA,
        "architecture_version": version,
        "source_count": len(sources),
        "source_set_sha256": source_set.hexdigest(),
        "sources": sources,
        "diagrams": diagrams,
    }


def manifest_text(root: Path = ROOT) -> str:
    return (
        json.dumps(
            build_manifest(root),
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        + "\n"
    )


def write_manifest(root: Path = ROOT) -> None:
    destination = root / MANIFEST_PATH
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(manifest_text(root), encoding="utf-8")
    print(f"wrote {MANIFEST_PATH.as_posix()}")


def check_manifest(root: Path = ROOT) -> bool:
    expected = manifest_text(root)
    path = root / MANIFEST_PATH
    if path.is_file() and path.read_text(encoding="utf-8") == expected:
        print("architecture manifest is current")
        return True
    print(
        f"architecture manifest requires refresh: {MANIFEST_PATH.as_posix()}",
        file=sys.stderr,
    )
    return False


def _git(root: Path, *args: str) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=root,
        text=True,
        capture_output=True,
    )
    if result.returncode:
        raise ValueError(
            result.stderr.strip() or f"git {' '.join(args)} failed"
        )
    return result.stdout.strip()


def _base_file(root: Path, base_ref: str, path: Path) -> str | None:
    result = subprocess.run(
        ["git", "show", f"{base_ref}:{path.as_posix()}"],
        cwd=root,
        text=True,
        capture_output=True,
    )
    return result.stdout.strip() if result.returncode == 0 else None


def _is_architecture_source(path: str) -> bool:
    if path in {
        "architecture.md",
        SHE_DIAGRAM.as_posix(),
        VERSION_PATH.as_posix(),
    }:
        return True
    if (
        path.startswith("docs/architecture/")
        and not path.startswith("docs/architecture/generated/")
    ):
        return Path(path).suffix.lower() in {".md", ".mmd"}
    return (
        path.startswith("docs/ops/diagrams/")
        and path.endswith(".mmd")
    )


def check_version_bump(
    root: Path = ROOT,
    base_ref: str = "origin/master",
) -> bool:
    changed = set(filter(
        None,
        _git(root, "diff", "--name-only", f"{base_ref}...HEAD").splitlines(),
    ))
    semantic_changes = sorted(
        path for path in changed if _is_architecture_source(path)
    )
    if not semantic_changes:
        print("architecture source unchanged; version bump not required")
        return True

    required = {
        VERSION_PATH.as_posix(),
        CHANGELOG_PATH.as_posix(),
    }
    missing = sorted(required - changed)
    if missing:
        raise ValueError(
            "semantic architecture changes require VERSION and CHANGELOG "
            "updates in the same change: " + ", ".join(missing)
        )

    current, current_tuple = _read_version(root)
    previous_raw = _base_file(root, base_ref, VERSION_PATH)
    if previous_raw is None:
        if current != "1.0.0":
            raise ValueError(
                "initial architecture baseline must start at 1.0.0"
            )
    else:
        previous_match = SEMVER.fullmatch(previous_raw)
        if not previous_match:
            raise ValueError(
                f"base architecture version is invalid: {previous_raw!r}"
            )
        previous_tuple = tuple(
            int(part) for part in previous_match.groups()
        )
        if current_tuple <= previous_tuple:
            raise ValueError(
                f"increase architecture version above {previous_raw}; "
                f"current is {current}"
            )

    changelog = (root / CHANGELOG_PATH).read_text(encoding="utf-8")
    heading = (
        rf"^##\s+\[{re.escape(current)}\](?:\s|$)"
        rf"|^##\s+{re.escape(current)}(?:\s|$)"
    )
    if not re.search(heading, changelog, re.MULTILINE):
        raise ValueError(
            f"CHANGELOG.md requires a heading for architecture version {current}"
        )

    print(
        f"architecture version bump validated: "
        f"{previous_raw or 'unreleased'} -> {current}"
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument(
        "--write",
        action="store_true",
        help="generate the deterministic architecture manifest",
    )
    action.add_argument(
        "--check",
        action="store_true",
        help="fail when the committed manifest is stale",
    )
    parser.add_argument(
        "--check-version-from",
        help="require a version/changelog bump for semantic changes from this Git ref",
    )
    args = parser.parse_args()

    try:
        if args.check_version_from:
            check_version_bump(ROOT, args.check_version_from)
        if args.write:
            write_manifest(ROOT)
            return 0
        return 0 if check_manifest(ROOT) else 1
    except (OSError, ValueError) as exc:
        print(
            f"architecture documentation validation failed: {exc}",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
