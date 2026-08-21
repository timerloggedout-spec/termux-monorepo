#!/usr/bin/env python3
"""Render deterministic Linguist contact-document projections from *.hum.md sources.

The renderer protects Markdown link destinations and fenced-code bodies, then applies a
public bootstrap lexicon to display or machine contact surfaces. It is deliberately not
the private production mapper: that mapper remains operator-custodied and outside Git.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path
import re
import sys
from typing import Iterable


DISPLAY_LEXICON = {
    "agent": "4g3n7",
    "agents": "4g3n75",
    "agentic": "4g3n71c",
    "branch": "br4nch",
    "claude": "cl4ud3",
    "command": "c0mm4nd",
    "compression": "c0mpr35510n",
    "context": "c0n73x7",
    "directory": "d1r3c70ry",
    "documentation": "d0cum3n74710n",
    "file": "f1l3",
    "files": "f1l35",
    "fork": "f0rk",
    "grimoire": "gr1m01r3",
    "human": "hum4n",
    "integration": "1n73gr4710n",
    "language": "l4ngu4g3",
    "machine": "m4ch1n3",
    "name": "n4m3",
    "names": "n4m35",
    "obfuscation": "0bfu5c4710n",
    "path": "p47h",
    "paths": "p47h5",
    "pointer": "p01n73r",
    "probe": "pr0b3",
    "process": "pr0c355",
    "project": "pr0j3c7",
    "projects": "pr0j3c75",
    "repository": "r3p05170ry",
    "repositories": "r3p05170r135",
    "review": "r3v13w",
    "security": "53cur17y",
    "system": "5y573m",
    "validation": "v4l1d4710n",
    "value": "v4lu3",
    "values": "v4lu35",
    "verify": "v3r1fy",
    "workflow": "w0rkfl0w",
    "workflows": "w0rkfl0w5",
}

MACHINE_LEXICON = {
    "agent": "§01§", "agents": "§02§", "agentic": "§03§", "branch": "§04§",
    "claude": "§05§", "command": "§06§", "compression": "§07§", "context": "§08§",
    "directory": "§09§", "documentation": "§0a§", "file": "§0b§", "fork": "§0c§",
    "grimoire": "§0d§", "human": "§0e§", "integration": "§0f§", "language": "§10§",
    "machine": "§11§", "name": "§12§", "obfuscation": "§13§", "path": "§14§",
    "pointer": "§15§", "probe": "§16§", "process": "§17§", "project": "§18§",
    "repository": "§19§", "review": "§1a§", "security": "§1b§", "system": "§1c§",
    "validation": "§1d§", "value": "§1e§", "verify": "§1f§", "workflow": "§20§",
    "files": "§a1§", "names": "§a2§", "paths": "§a3§", "values": "§a4§",
    "projects": "§a5§", "repositories": "§a6§", "workflows": "§a7§",
}

FENCED_CODE = re.compile(r"(?ms)^ {0,3}(```|~~~).*?^ {0,3}\1[^\n]*$")
LINK_DESTINATION = re.compile(r"(\]\()([^\n)]*)(\))")
LEXICON_PATTERN = re.compile(
    r"(?<![\w-])(?:" + "|".join(re.escape(term) for term in sorted(DISPLAY_LEXICON, key=len, reverse=True)) + r")(?![\w-])",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Projection:
    source: Path
    target: Path
    mode: str


def _normalize(text: str) -> str:
    return text.replace("\r\n", "\n").replace("\r", "\n").rstrip() + "\n"


def _projection_mode(source: Path) -> str:
    return "display-l33t-v1" if source.as_posix() == "README.hum.md" else "machine-grimoire-seed-v1"


def _target_for(source: Path) -> Path:
    name = source.name
    if not name.endswith(".hum.md"):
        raise ValueError(f"not a human projection source: {source}")
    return source.with_name(name.replace(".hum.md", ".md"))


def discover(root: Path) -> list[Projection]:
    sources = [
        root / "README.hum.md",
        root / "AGENTS.hum.md",
        root / "CLAUDE.hum.md",
    ]
    sources.extend(sorted((root / "docs" / "icm").rglob("*.hum.md")))
    projections = []
    for source in sources:
        if source.exists():
            projections.append(
                Projection(
                    source=source.relative_to(root),
                    target=_target_for(source.relative_to(root)),
                    mode=_projection_mode(source.relative_to(root)),
                )
            )
    return projections


def _protect_structural_spans(text: str) -> tuple[str, list[str]]:
    protected: list[str] = []

    def stash(value: str) -> str:
        token = f"\ue000{len(protected)}\ue001"
        protected.append(value)
        return token

    text = FENCED_CODE.sub(lambda match: stash(match.group(0)), text)
    text = LINK_DESTINATION.sub(lambda match: match.group(1) + stash(match.group(2)) + match.group(3), text)
    return text, protected


def _restore_structural_spans(text: str, protected: Iterable[str]) -> str:
    for index, value in enumerate(protected):
        text = text.replace(f"\ue000{index}\ue001", value)
    return text


def _replace_with_lexicon(text: str, mode: str) -> str:
    lexicon = DISPLAY_LEXICON if mode == "display-l33t-v1" else MACHINE_LEXICON

    def replace(match: re.Match[str]) -> str:
        return lexicon[match.group(0).lower()]

    return LEXICON_PATTERN.sub(replace, text)


def render(source_text: str, source: Path, mode: str) -> str:
    protected_text, protected = _protect_structural_spans(_normalize(source_text))
    rendered = _replace_with_lexicon(protected_text, mode)
    rendered = _restore_structural_spans(rendered, protected)
    header = (
        "<!-- LinguistProjection: generated; "
        f"source={source.as_posix()}; mode={mode}; "
        "structural-exceptions=fenced-code,markdown-link-destinations -->\n\n"
    )
    return header + rendered


def write_or_check(root: Path, check: bool) -> int:
    stale: list[str] = []
    for projection in discover(root):
        source_path = root / projection.source
        target_path = root / projection.target
        expected = render(source_path.read_text(encoding="utf-8"), projection.source, projection.mode)
        actual = target_path.read_text(encoding="utf-8") if target_path.exists() else None
        if actual != expected:
            stale.append(projection.target.as_posix())
            if not check:
                target_path.write_text(expected, encoding="utf-8")
    if stale and check:
        print("stale Linguist projections:", ", ".join(stale), file=sys.stderr)
        return 1
    print(f"Linguist projections {'verified' if check else 'rendered'}: {len(discover(root))}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd(), help="repository root")
    parser.add_argument("--check", action="store_true", help="fail when a projection is stale")
    args = parser.parse_args()
    return write_or_check(args.root.resolve(), args.check)


if __name__ == "__main__":
    raise SystemExit(main())
