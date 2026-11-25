#!/usr/bin/env python3
"""Render and verify the explicit Agent-machine to human-source pair registry.

The current projection is byte-preserving identity: each machine surface has a
reviewable sibling ``*.hum.md`` source, and every pair remains independently
registered. A future reversible notation requires an approved codec and its own
round-trip fixtures before replacing this projection.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import sys
import tempfile
from typing import Iterable


@dataclass(frozen=True)
class Projection:
    source: Path
    target: Path


# Keep every active Agent machine surface explicit, including ICM alias files.
PAIR_REGISTRY: tuple[Projection, ...] = (
    Projection(Path("CLAUDE.hum.md"), Path("CLAUDE.md")),
    Projection(Path("GEMINI.hum.md"), Path("GEMINI.md")),
    Projection(Path(".codex/AGENTS.hum.md"), Path(".codex/AGENTS.md")),
    Projection(Path("docs/icm/CLAUDE.hum.md"), Path("docs/icm/CLAUDE.md")),
    Projection(Path("docs/icm/AGENTS.hum.md"), Path("docs/icm/AGENTS.md")),
    Projection(
        Path("docs/icm/maintenance/CLAUDE.hum.md"),
        Path("docs/icm/maintenance/CLAUDE.md"),
    ),
    Projection(
        Path("docs/icm/maintenance/AGENTS.hum.md"),
        Path("docs/icm/maintenance/AGENTS.md"),
    ),
)

_CREDENTIAL_PATTERNS = tuple(
    re.compile(pattern, re.IGNORECASE)
    for pattern in (
        r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----",
        r"\b(?:gh[pousr]_[A-Za-z0-9]{20,}|github_pat_[A-Za-z0-9_]{20,})\b",
        r"\bsk-[A-Za-z0-9_-]{20,}\b",
        r"\bAKIA[0-9A-Z]{16}\b",
        r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b",
        r"\b[A-Z0-9_-]*(?:API[_-]?KEY|ACCESS[_-]?TOKEN|AUTH[_-]?TOKEN|CLIENT[_-]?SECRET|PASSWORD|SECRET|TOKEN)\s*[:=]\s*['\"]?(?!<)[A-Za-z0-9/+=._-]{12,}",
        r"\b(?:api[_-]?key|access[_-]?token|client[_-]?secret|password)\s*[:=]\s*['\"]?[A-Za-z0-9/+=._-]{16,}",
    )
)


class ProjectionError(ValueError):
    """Raised when the registry or any input path fails safe preflight."""


def render(source_bytes: bytes, source: Path) -> bytes:
    """Return the reviewed source byte-for-byte until a reversible codec is approved."""
    if not isinstance(source_bytes, bytes):
        raise TypeError("projection input must be bytes")
    if not source.as_posix().endswith(".hum.md"):
        raise ProjectionError(f"projection source must end in .hum.md: {source}")
    return source_bytes


def _relative_parts(path: Path, role: str) -> tuple[str, ...]:
    raw = path.as_posix()
    parsed = PurePosixPath(raw)
    if not raw or parsed.is_absolute() or "\\" in raw:
        raise ProjectionError(f"{role} path must be repository-relative: {raw!r}")
    parts = parsed.parts
    if not parts or any(part in ("", ".", "..") for part in parts):
        raise ProjectionError(f"{role} path has an unsafe component: {raw!r}")
    return parts


def _check_no_symlink_components(root: Path, relative: Path, role: str) -> Path:
    current = root
    for part in _relative_parts(relative, role):
        current = current / part
        if current.is_symlink():
            raise ProjectionError(f"{role} path contains a symlink: {relative.as_posix()}")
        resolved = current.resolve(strict=False)
        try:
            resolved.relative_to(root)
        except ValueError as exc:
            raise ProjectionError(f"{role} path escapes repository root: {relative.as_posix()}") from exc
    return current


def validate_registry(
    root: Path,
    projections: Iterable[Projection] | None = None,
) -> tuple[Projection, ...]:
    """Validate exact scope, uniqueness, sibling naming, containment, and filesystem type."""
    root_input = Path(root).absolute()
    if root_input.is_symlink():
        raise ProjectionError("repository root must not be a symlink")
    root_path = root_input.resolve(strict=True)
    if not root_path.is_dir():
        raise ProjectionError(f"repository root is not a directory: {root_path}")

    registry = tuple(PAIR_REGISTRY if projections is None else projections)
    if len(registry) != 7:
        raise ProjectionError(f"expected exactly seven Agent pairs, found {len(registry)}")

    seen_sources: set[str] = set()
    seen_targets: set[str] = set()
    checked: list[Projection] = []
    for projection in registry:
        source = Path(projection.source)
        target = Path(projection.target)
        source_name = source.as_posix()
        target_name = target.as_posix()
        if source_name in seen_sources or target_name in seen_targets:
            raise ProjectionError("registry source and target paths must each be unique")
        seen_sources.add(source_name)
        seen_targets.add(target_name)
        _relative_parts(source, "source")
        _relative_parts(target, "target")
        if not source_name.endswith(".hum.md"):
            raise ProjectionError(f"source must end in .hum.md: {source_name}")
        expected_target = source_name.removesuffix(".hum.md") + ".md"
        if target_name != expected_target:
            raise ProjectionError(f"target must be the source sibling {expected_target}: {target_name}")
        source_path = _check_no_symlink_components(root_path, source, "source")
        target_path = _check_no_symlink_components(root_path, target, "target")
        if not source_path.is_file():
            raise ProjectionError(f"source is missing or not a regular file: {source_name}")
        if target_path.exists() and not target_path.is_file():
            raise ProjectionError(f"target is not a regular file: {target_name}")
        checked.append(Projection(source, target))

    return tuple(checked)


def _decode_and_screen(source_bytes: bytes, source: Path) -> None:
    try:
        text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectionError(f"source is not valid UTF-8: {source.as_posix()}") from exc
    for pattern in _CREDENTIAL_PATTERNS:
        if pattern.search(text):
            raise ProjectionError(f"credential-like content rejected in {source.as_posix()}")


def _atomic_replace(target: Path, payload: bytes) -> None:
    mode = target.stat().st_mode & 0o777 if target.exists() else 0o644
    temp_path: Path | None = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="wb",
            prefix=f".{target.name}.",
            suffix=".tmp",
            dir=target.parent,
            delete=False,
        ) as stream:
            temp_path = Path(stream.name)
            stream.write(payload)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp_path, mode)
        os.replace(temp_path, target)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def write_or_check(root: Path, check: bool) -> int:
    """Preflight every pair, then verify parity or atomically render all stale targets."""
    root_path = Path(root).absolute()
    registry = validate_registry(root_path)
    root_path = root_path.resolve(strict=True)

    # Read and screen every source before the first target mutation.
    rendered: list[tuple[Projection, bytes]] = []
    for projection in registry:
        source_path = root_path / projection.source
        source_bytes = source_path.read_bytes()
        _decode_and_screen(source_bytes, projection.source)
        rendered.append((projection, render(source_bytes, projection.source)))

    stale: list[str] = []
    for projection, expected in rendered:
        target_path = root_path / projection.target
        actual = target_path.read_bytes() if target_path.exists() else None
        if actual != expected:
            stale.append(projection.target.as_posix())

    if check:
        if stale:
            print("stale Linguist pairs: " + ", ".join(stale), file=sys.stderr)
            return 1
        print(f"Linguist pairs verified: {len(registry)}")
        return 0

    for projection, expected in rendered:
        target_path = root_path / projection.target
        actual = target_path.read_bytes() if target_path.exists() else None
        if actual != expected:
            _atomic_replace(target_path, expected)
    print(f"Linguist pairs rendered: {len(registry)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--check", action="store_true", help="fail when a pair is stale")
    args = parser.parse_args(argv)
    try:
        return write_or_check(args.root, check=args.check)
    except (OSError, ProjectionError, ValueError) as exc:
        print(f"Linguist pair validation failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
