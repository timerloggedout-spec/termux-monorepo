#!/usr/bin/env python3
"""Render and verify explicit per-lane Linguist contracts for Agent documents."""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import tempfile
from typing import Iterable

ROOT = Path(__file__).resolve().parents[2]

RELATIONSHIP_CLASSES = frozenset(
    {
        "direct projection",
        "compatibility/tooling surface",
        "historical rename",
        "independent entry",
        "pending migration",
        "excluded with rationale",
    }
)
MAPPING_MODES = frozenset({"identity", "siglary-operators"})
SIGLARY_OPERATOR_SUBSTITUTIONS = (("and", "∧"), ("or", "∨"))
SIGLARY_PENDING_SEQUENCE_SEPARATOR = "→"
_SIGLARY_CONNECTIVE_RE = re.compile(r"\band/or\b|\b(?P<word>and|or)\b", re.IGNORECASE)
_INLINE_PROTECTED_RE = re.compile(
    r"`+[^`\n]*`+|https?://[^\s)>\]]+|\]\((?:\\.|[^)\n])*\)|"
    r'"(?:\\.|[^"\\\n])*"|“[^”\n]*”|‘[^’\n]*’|'
    r"(?<![\w])'[^'\n]+'(?!\w)|<[^>\n]+>",
    re.IGNORECASE,
)
_FENCE_RE = re.compile(r"^ {0,3}(`{3,}|~{3,})(.*)$")


@dataclass(frozen=True)
class Projection:
    pair_id: str
    lane: str
    source: Path
    target: Path
    relationship_class: str
    mapping_mode: str
    alias_group: str | None = None
    historical_aliases: tuple[str, ...] = ()
    historical_alias_relationship_class: str = ""
    provenance_note: str = ""


# Muse initiated the naming migration per owner-supplied attribution; repository verification is pending.
PAIR_REGISTRY: tuple[Projection, ...] = (
    Projection(
        pair_id="root-claude",
        lane="root-claude",
        source=Path("CLAUDE.hum.md"),
        target=Path("CLAUDE.md"),
        relationship_class="direct projection",
        mapping_mode="siglary-operators",
        historical_aliases=("AGENTS.hum.md", "AGENTS.md"),
        historical_alias_relationship_class="historical rename",
        provenance_note=(
            "Muse initiated the naming migration (owner-supplied attribution; "
            "repository verification pending)."
        ),
    ),
    Projection(
        pair_id="root-gemini",
        lane="root-gemini",
        source=Path("GEMINI.hum.md"),
        target=Path("GEMINI.md"),
        relationship_class="direct projection",
        mapping_mode="identity",
    ),
    Projection(
        pair_id="codex-compatibility",
        lane="codex-compatibility",
        source=Path(".codex/AGENTS.hum.md"),
        target=Path(".codex/AGENTS.md"),
        relationship_class="compatibility/tooling surface",
        mapping_mode="identity",
    ),
    Projection(
        pair_id="icm-claude",
        lane="icm-claude",
        source=Path("docs/icm/CLAUDE.hum.md"),
        target=Path("docs/icm/CLAUDE.md"),
        relationship_class="direct projection",
        mapping_mode="siglary-operators",
        alias_group="icm-machine-aliases",
    ),
    Projection(
        pair_id="icm-agents",
        lane="icm-agents",
        source=Path("docs/icm/AGENTS.hum.md"),
        target=Path("docs/icm/AGENTS.md"),
        relationship_class="compatibility/tooling surface",
        mapping_mode="siglary-operators",
        alias_group="icm-machine-aliases",
    ),
    Projection(
        pair_id="icm-maintenance-claude",
        lane="icm-maintenance-claude",
        source=Path("docs/icm/maintenance/CLAUDE.hum.md"),
        target=Path("docs/icm/maintenance/CLAUDE.md"),
        relationship_class="direct projection",
        mapping_mode="siglary-operators",
        alias_group="icm-maintenance-machine-aliases",
    ),
    Projection(
        pair_id="icm-maintenance-agents",
        lane="icm-maintenance-agents",
        source=Path("docs/icm/maintenance/AGENTS.hum.md"),
        target=Path("docs/icm/maintenance/AGENTS.md"),
        relationship_class="compatibility/tooling surface",
        mapping_mode="siglary-operators",
        alias_group="icm-maintenance-machine-aliases",
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
    root: Path = ROOT,
    projections: Iterable[Projection] | None = None,
) -> tuple[Projection, ...]:
    """Validate lane metadata, exact scope, uniqueness, containment, and filesystem type."""
    root_input = Path(root).absolute()
    if root_input.is_symlink():
        raise ProjectionError("repository root must not be a symlink")
    root_path = root_input.resolve(strict=True)
    if not root_path.is_dir():
        raise ProjectionError(f"repository root is not a directory: {root_path}")

    registry = tuple(PAIR_REGISTRY if projections is None else projections)
    if len(registry) != 7:
        raise ProjectionError(f"expected exactly seven Agent pairs, found {len(registry)}")

    seen_ids: set[str] = set()
    seen_lanes: set[str] = set()
    seen_sources: set[str] = set()
    seen_targets: set[str] = set()
    alias_members: dict[str, list[Projection]] = {}
    checked: list[Projection] = []
    for projection in registry:
        if not projection.pair_id or projection.pair_id in seen_ids:
            raise ProjectionError(f"pair ids must be non-empty and unique: {projection.pair_id!r}")
        if not projection.lane or projection.lane in seen_lanes:
            raise ProjectionError(f"lane ids must be non-empty and unique: {projection.lane!r}")
        seen_ids.add(projection.pair_id)
        seen_lanes.add(projection.lane)
        if projection.relationship_class not in RELATIONSHIP_CLASSES:
            raise ProjectionError(
                f"{projection.pair_id}: unsupported relationship class "
                f"{projection.relationship_class!r}"
            )
        if projection.relationship_class == "excluded with rationale":
            raise ProjectionError(f"{projection.pair_id}: excluded entries cannot be active projections")
        if projection.mapping_mode not in MAPPING_MODES:
            raise ProjectionError(
                f"{projection.pair_id}: unsupported mapping mode {projection.mapping_mode!r}"
            )

        source = Path(projection.source)
        target = Path(projection.target)
        source_name = source.as_posix()
        target_name = target.as_posix()
        if source_name in seen_sources or target_name in seen_targets:
            raise ProjectionError("registry source and target paths must each be unique")
        seen_sources.add(source_name)
        seen_targets.add(target_name)
        source_parts = _relative_parts(source, "source")
        target_parts = _relative_parts(target, "target")
        if not source_name.endswith(".hum.md"):
            raise ProjectionError(f"source must end in .hum.md: {source_name}")
        expected_target = source_name.removesuffix(".hum.md") + ".md"
        if target_name != expected_target:
            raise ProjectionError(f"target must be the source sibling {expected_target}: {target_name}")
        if source_parts[:-1] != target_parts[:-1]:
            raise ProjectionError(f"{projection.pair_id}: source and target must be siblings")

        for alias in projection.historical_aliases:
            _relative_parts(Path(alias), "historical alias")
        if projection.historical_aliases:
            if projection.historical_alias_relationship_class != "historical rename":
                raise ProjectionError(
                    f"{projection.pair_id}: historical aliases require the historical rename class"
                )
        elif projection.historical_alias_relationship_class:
            raise ProjectionError(
                f"{projection.pair_id}: historical alias class has no alias paths"
            )

        source_path = _check_no_symlink_components(root_path, source, "source")
        target_path = _check_no_symlink_components(root_path, target, "target")
        if not source_path.is_file():
            raise ProjectionError(f"source is missing or not a regular file: {source_name}")
        if target_path.exists() and not target_path.is_file():
            raise ProjectionError(f"target is not a regular file: {target_name}")
        if projection.alias_group:
            alias_members.setdefault(projection.alias_group, []).append(projection)
        checked.append(projection)

    for group, members in alias_members.items():
        if len(members) != 2:
            raise ProjectionError(f"alias group {group!r} must contain exactly two projections")
        if members[0].source.parent != members[1].source.parent:
            raise ProjectionError(f"alias group {group!r} spans multiple directories")

    return tuple(checked)


def _replace_siglary_connectives(segment: str) -> str:
    """Use registered operators and expand the pending sequence marker to a plain word."""
    substitutions = dict(SIGLARY_OPERATOR_SUBSTITUTIONS)

    def replace(match: re.Match[str]) -> str:
        token = match.group(0)
        folded = token.casefold()
        if folded == "and/or":
            return token
        prefix = segment[: match.start()]
        if re.search(r"[,;:]\s+$", prefix):
            return token  # preserve the conjunction in a serial list
        if folded == "or" and re.search(r"\beither\b[^;.!?\n]*$", prefix, re.IGNORECASE):
            return token  # preserve the exclusive either/or construction
        return substitutions[folded]

    operatorized = _SIGLARY_CONNECTIVE_RE.sub(replace, segment)
    separator = re.escape(SIGLARY_PENDING_SEQUENCE_SEPARATOR)
    return re.sub(rf"\s*{separator}\s*", " then ", operatorized)


def _transform_inline_prose(segment: str, *, transform: bool) -> str:
    if not transform:
        return segment
    pieces: list[str] = []
    cursor = 0
    for match in _INLINE_PROTECTED_RE.finditer(segment):
        pieces.append(_replace_siglary_connectives(segment[cursor : match.start()]))
        pieces.append(match.group(0))
        cursor = match.end()
    pieces.append(_replace_siglary_connectives(segment[cursor:]))
    return "".join(pieces)


def _transform_prose_line(
    line: str,
    in_html_comment: bool,
    *,
    transform: bool,
) -> tuple[str, bool]:
    """Transform prose outside comments and protected inline Markdown spans."""
    output: list[str] = []
    cursor = 0
    while cursor < len(line):
        if in_html_comment:
            end = line.find("-->", cursor)
            if end < 0:
                output.append(line[cursor:])
                return "".join(output), True
            output.append(line[cursor : end + 3])
            cursor = end + 3
            in_html_comment = False
            continue

        start = line.find("<!--", cursor)
        inline = _INLINE_PROTECTED_RE.search(line, cursor)
        if inline and (start < 0 or inline.start() < start):
            prose = line[cursor : inline.start()]
            output.append(_transform_inline_prose(prose, transform=transform))
            output.append(inline.group(0))
            cursor = inline.end()
            continue
        if start < 0:
            output.append(_transform_inline_prose(line[cursor:], transform=transform))
            break
        output.append(_transform_inline_prose(line[cursor:start], transform=transform))
        end = line.find("-->", start + 4)
        if end < 0:
            output.append(line[start:])
            return "".join(output), True
        output.append(line[start : end + 3])
        cursor = end + 3
    return "".join(output), in_html_comment


def _siglary_operator_projection(source_bytes: bytes, source: Path) -> bytes:
    """Map registered prose operators; preserve literals and expand pending notation."""
    try:
        text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectionError(f"source is not valid UTF-8: {source.as_posix()}") from exc

    output: list[str] = []
    in_front_matter = False
    in_fence: tuple[str, int] | None = None
    in_html_comment = False
    lines = text.splitlines(keepends=True)
    for number, line in enumerate(lines):
        body = line.rstrip("\r\n")
        if number == 0 and body == "---":
            in_front_matter = True
            output.append(line)
            continue
        if in_front_matter:
            output.append(line)
            if body in {"---", "..."}:
                in_front_matter = False
            continue

        if in_fence is not None:
            output.append(line)
            marker, minimum_length = in_fence
            closing = _FENCE_RE.match(body)
            if (
                closing
                and closing.group(1)[0] == marker
                and len(closing.group(1)) >= minimum_length
                and not closing.group(2).strip()
            ):
                in_fence = None
            continue

        opening = _FENCE_RE.match(body) if not in_html_comment else None
        if opening:
            output.append(line)
            in_fence = (opening.group(1)[0], len(opening.group(1)))
            continue

        literal_line = body.lstrip().startswith(">") or line.startswith("\t") or body.startswith("    ")
        if literal_line and not in_html_comment:
            output.append(line)
            continue
        rendered, in_html_comment = _transform_prose_line(
            line,
            in_html_comment,
            transform=not literal_line,
        )
        output.append(rendered)

    return "".join(output).encode("utf-8")


def render(source_bytes: bytes, projection: Projection) -> bytes:
    """Apply only the mapping mode explicitly assigned to this lane."""
    if not isinstance(source_bytes, bytes):
        raise TypeError("projection input must be bytes")
    if not projection.source.as_posix().endswith(".hum.md"):
        raise ProjectionError(f"projection source must end in .hum.md: {projection.source}")
    if projection.mapping_mode == "identity":
        return source_bytes
    if projection.mapping_mode == "siglary-operators":
        return _siglary_operator_projection(source_bytes, projection.source)
    raise ProjectionError(
        f"{projection.pair_id}: mapping mode {projection.mapping_mode!r} has no renderer"
    )


def _decode_and_screen(source_bytes: bytes, source: Path) -> None:
    try:
        text = source_bytes.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise ProjectionError(f"source is not valid UTF-8: {source.as_posix()}") from exc
    for pattern in _CREDENTIAL_PATTERNS:
        if pattern.search(text):
            raise ProjectionError(f"credential-like content rejected in {source.as_posix()}")


def _safe_mode(target: Path) -> int:
    """Keep owner read/write; preserve only existing group/other read access."""
    mode = 0o640
    if target.exists():
        mode = 0o600 | (stat.S_IMODE(target.stat().st_mode) & 0o040)
    return mode


def _atomic_replace(target: Path, payload: bytes) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    mode = _safe_mode(target)
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
            os.fchmod(stream.fileno(), mode)
        os.replace(temp_path, target)
        temp_path = None
    finally:
        if temp_path is not None:
            try:
                temp_path.unlink()
            except FileNotFoundError:
                pass


def _alias_preflight(rendered: list[tuple[Projection, bytes]]) -> None:
    groups: dict[str, list[tuple[Projection, bytes]]] = {}
    for projection, payload in rendered:
        if projection.alias_group:
            groups.setdefault(projection.alias_group, []).append((projection, payload))
    for group, members in groups.items():
        first_projection, first_payload = members[0]
        for projection, payload in members[1:]:
            if payload != first_payload:
                raise ProjectionError(
                    f"alias group {group!r} has divergent rendered sources: "
                    f"{first_projection.source.as_posix()} and {projection.source.as_posix()}"
                )


def write_or_check(root: Path = ROOT, *, check: bool = False) -> int:
    """Preflight every lane and alias group before verifying or writing any target."""
    root_path = Path(root).absolute()
    registry = validate_registry(root_path)
    root_path = root_path.resolve(strict=True)

    rendered: list[tuple[Projection, bytes]] = []
    for projection in registry:
        source_path = root_path / projection.source
        source_bytes = source_path.read_bytes()
        _decode_and_screen(source_bytes, projection.source)
        rendered.append((projection, render(source_bytes, projection)))

    # Machine aliases are compared as a complete batch before any target mutation.
    _alias_preflight(rendered)

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
