#!/usr/bin/env python3
"""Collect repository-bounded source relationships for the context graph.

Only metadata needed for navigation is emitted.  The collector never reads or
emits sensitive/session/browser content and records parser coverage explicitly.
"""

from __future__ import annotations

import argparse
import ast
import fnmatch
import json
import os
import sys
import warnings
from collections.abc import Iterable, Mapping
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath
from typing import Any

try:
    from .compiler import CompilationError, load_json, path_is_sensitive
except ImportError:  # Supports direct `python path/to/source_collector.py` use.
    from compiler import CompilationError, load_json, path_is_sensitive

COLLECTOR_ID = "archwiz.context_relationships.source_collector@1.0"
SUPPORTED_LANGUAGES = {".py": "python"}


@dataclass
class SourceReport:
    scanned_files: int = 0
    source_files: int = 0
    excluded_files: int = 0
    oversized_files: int = 0
    unsupported_files: int = 0
    parser_failures: list[dict[str, str]] = field(default_factory=list)
    unavailable_files: int = 0
    scopes_matched: int = 0

    def as_dict(self) -> dict[str, Any]:
        return {
            "collector": COLLECTOR_ID,
            "scanned_files": self.scanned_files,
            "source_files": self.source_files,
            "excluded_files": self.excluded_files,
            "oversized_files": self.oversized_files,
            "unsupported_files": self.unsupported_files,
            "parser_failures": sorted(self.parser_failures, key=lambda item: item["path"]),
            "unavailable_files": self.unavailable_files,
            "scopes_matched": self.scopes_matched,
        }


def utc_from_epoch(seconds: float) -> str:
    return datetime.fromtimestamp(seconds, timezone.utc).isoformat().replace("+00:00", "Z")


def repository_url(owner: str, name: str, ref: str, relative_path: str) -> str:
    return f"https://github.com/{owner}/{name}/blob/{ref}/{relative_path}"


def normalize_relative(path: Path, root: Path) -> str:
    return path.relative_to(root).as_posix()


def matches_path(relative_path: str, patterns: Iterable[str]) -> bool:
    return any(fnmatch.fnmatch(relative_path, pattern) for pattern in patterns)


def local_import_target(module: str, level: int, source_path: str, files: set[str]) -> str | None:
    """Resolve a Python import to a tracked local module when the mapping is exact."""
    source_parent = PurePosixPath(source_path).parent
    if level:
        for _ in range(max(level - 1, 0)):
            source_parent = source_parent.parent
    candidates: list[PurePosixPath] = []
    if module:
        candidates.append(source_parent / f"{module.replace('.', '/')}.py")
        candidates.append(source_parent / module.replace(".", "/") / "__init__.py")
        candidates.append(PurePosixPath(f"{module.replace('.', '/')}.py"))
        candidates.append(PurePosixPath(module.replace(".", "/")) / "__init__.py")
    for candidate in candidates:
        normalized = candidate.as_posix().lstrip("./")
        if normalized in files:
            return normalized
    return None


class SymbolCollector(ast.NodeVisitor):
    def __init__(self, relative_path: str) -> None:
        self.relative_path = relative_path
        self.stack: list[str] = []
        self.symbols: list[dict[str, Any]] = []

    def _add(self, node: ast.AST, kind: str, name: str) -> None:
        qualname = ".".join([*self.stack, name]) if self.stack else name
        self.symbols.append(
            {
                "kind": "symbol",
                "external_id": f"{self.relative_path}:{qualname}:{getattr(node, 'lineno', 0)}",
                "attributes": {
                    "path": self.relative_path,
                    "language": "python",
                    "symbol_kind": kind,
                    "name": name,
                    "qualname": qualname,
                    "line": getattr(node, "lineno", 0),
                    "end_line": getattr(node, "end_lineno", getattr(node, "lineno", 0)),
                },
            }
        )

    def visit_ClassDef(self, node: ast.ClassDef) -> None:
        self._add(node, "class", node.name)
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._add(node, "function", node.name)
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._add(node, "async_function", node.name)
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()


def load_scope_registry(path: Path) -> tuple[list[str], int, list[Mapping[str, Any]]]:
    registry = load_json(path, "scope registry")
    exclusions = registry.get("exclusions", {})
    if not isinstance(exclusions, Mapping):
        raise CompilationError("scope registry exclusions must be an object")
    patterns = exclusions.get("path_globs", [])
    if not isinstance(patterns, list) or not all(isinstance(item, str) for item in patterns):
        raise CompilationError("scope registry exclusions.path_globs must be a string list")
    max_file_bytes = exclusions.get("max_file_bytes", 500000)
    if not isinstance(max_file_bytes, int) or max_file_bytes < 1:
        raise CompilationError("scope registry exclusions.max_file_bytes must be a positive integer")
    scopes = registry.get("scopes", [])
    if not isinstance(scopes, list):
        raise CompilationError("scope registry scopes must be an array")
    for scope in scopes:
        if not isinstance(scope, Mapping) or not isinstance(scope.get("id"), str):
            raise CompilationError("each scope must have a string id")
    return sorted(patterns), max_file_bytes, scopes


def iter_files(root: Path) -> Iterable[Path]:
    for directory, dirnames, filenames in os.walk(root, topdown=True, followlinks=False):
        dirnames[:] = sorted(name for name in dirnames if name != ".git")
        for filename in sorted(filenames):
            yield Path(directory) / filename


def collect_source_seed(
    root: Path,
    owner: str,
    name: str,
    ref: str,
    scope_registry_path: Path,
) -> tuple[dict[str, Any], dict[str, Any]]:
    """Collect exact local Python source relations into a compiler-compatible seed."""
    root = root.resolve()
    exclusions, max_file_bytes, scopes = load_scope_registry(scope_registry_path)
    registry_version = load_json(scope_registry_path, "scope registry").get("version")
    report = SourceReport()
    file_records: list[tuple[Path, str, str, int, float]] = []

    for path in iter_files(root):
        report.scanned_files += 1
        relative_path = normalize_relative(path, root)
        if path_is_sensitive(relative_path, exclusions):
            report.excluded_files += 1
            continue
        language = SUPPORTED_LANGUAGES.get(path.suffix.lower())
        if language is None:
            report.unsupported_files += 1
            continue
        try:
            stat = path.stat()
        except OSError:
            report.unavailable_files += 1
            continue
        if stat.st_size > max_file_bytes:
            report.oversized_files += 1
            continue
        file_records.append((path, relative_path, language, stat.st_size, stat.st_mtime))

    observed_at = utc_from_epoch(max((mtime for _, _, _, _, mtime in file_records), default=0))
    nodes: list[dict[str, Any]] = [
        {
            "kind": "repository",
            "external_id": f"{owner}/{name}",
            "url": f"https://github.com/{owner}/{name}",
            "observed_at": observed_at,
            "attributes": {"ref": ref},
        }
    ]
    edges: list[dict[str, Any]] = []
    local_files = {relative_path for _, relative_path, _, _, _ in file_records}

    for scope in scopes:
        nodes.append(
            {
                "kind": "scope",
                "external_id": scope["id"],
                "observed_at": observed_at,
                "attributes": {
                    "title": scope.get("title", scope["id"]),
                    "aliases": scope.get("aliases", []),
                    "registry_version": registry_version,
                },
            }
        )

    for path, relative_path, language, file_bytes, file_mtime in file_records:
        report.source_files += 1
        file_observed_at = utc_from_epoch(file_mtime)
        nodes.append(
            {
                "kind": "file",
                "external_id": relative_path,
                "url": repository_url(owner, name, ref, relative_path),
                "observed_at": file_observed_at,
                "attributes": {
                    "path": relative_path,
                    "language": language,
                    "bytes": file_bytes,
                },
            }
        )
        for scope in scopes:
            if matches_path(relative_path, scope.get("path_globs", [])):
                report.scopes_matched += 1
                edges.append(
                    {
                        "type": "IN_SCOPE",
                        "source": f"file:{relative_path}",
                        "target": f"scope:{scope['id']}",
                        "classification": "verified",
                        "observed_at": file_observed_at,
                        "evidence": [
                            {
                                "kind": "scope_registry",
                                "source": f"{scope_registry_path.as_posix()}#/scopes/{scope['id']}",
                                "collector": COLLECTOR_ID,
                                "details": {"matched_path": relative_path},
                            }
                        ],
                    }
                )
        try:
            with warnings.catch_warnings():
                warnings.simplefilter("ignore", SyntaxWarning)
                tree = ast.parse(path.read_text(encoding="utf-8"), filename=relative_path)
        except (OSError, UnicodeDecodeError, SyntaxError) as exc:
            report.parser_failures.append({"path": relative_path, "error": str(exc).splitlines()[0]})
            continue
        symbols = SymbolCollector(relative_path)
        symbols.visit(tree)
        for symbol in symbols.symbols:
            nodes.append(symbol)
            edges.append(
                {
                    "type": "DEFINES",
                    "source": f"file:{relative_path}",
                    "target": f"symbol:{symbol['external_id']}",
                    "classification": "verified",
                    "observed_at": file_observed_at,
                    "evidence": [
                        {
                            "kind": "ast",
                            "source": f"{relative_path}:{symbol['attributes']['line']}",
                            "collector": COLLECTOR_ID,
                            "details": {"symbol_kind": symbol["attributes"]["symbol_kind"]},
                        }
                    ],
                }
            )
        for ast_node in ast.walk(tree):
            if isinstance(ast_node, ast.Import):
                modules = [(alias.name, 0) for alias in ast_node.names]
            elif isinstance(ast_node, ast.ImportFrom):
                modules = (
                    [(ast_node.module, ast_node.level)]
                    if ast_node.module
                    else [(alias.name, ast_node.level) for alias in ast_node.names if alias.name != "*"]
                )
            else:
                continue
            for module, level in modules:
                target = local_import_target(module, level, relative_path, local_files)
                if target is None:
                    continue
                edges.append(
                    {
                        "type": "IMPORTS",
                        "source": f"file:{relative_path}",
                        "target": f"file:{target}",
                        "classification": "verified",
                        "observed_at": file_observed_at,
                        "evidence": [
                            {
                                "kind": "ast",
                                "source": f"{relative_path}:{getattr(ast_node, 'lineno', 0)}",
                                "collector": COLLECTOR_ID,
                                "details": {"module": module, "level": level},
                            }
                        ],
                    }
                )

    seed = {
        "schema_version": "1.0",
        "repository": {"owner": owner, "name": name, "default_branch": ref},
        "nodes": nodes,
        "edges": edges,
    }
    return seed, report.as_dict()


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."), help="Repository root to inspect")
    parser.add_argument("--owner", required=True, help="GitHub repository owner")
    parser.add_argument("--repo", required=True, help="GitHub repository name")
    parser.add_argument("--ref", required=True, help="Repository ref represented by this collection")
    parser.add_argument(
        "--scope-registry",
        type=Path,
        default=Path("config/context_relationships/scope_registry.json"),
    )
    parser.add_argument("--output", type=Path, required=True, help="Path for the normalized source seed")
    parser.add_argument("--report", type=Path, required=True, help="Path for parser coverage report")
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    try:
        seed, report = collect_source_seed(args.root, args.owner, args.repo, args.ref, args.scope_registry)
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.report.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(seed, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0
    except CompilationError as exc:
        print(f"source collection failed: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
