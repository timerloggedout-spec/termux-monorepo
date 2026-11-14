#!/usr/bin/env python3
"""Canonical proposal-package manifest and QDesk award consumer verifier."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
from pathlib import Path, PurePosixPath
from typing import Any

SCHEMA = "delphi-proposal-package/v1"
ALLOWED_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".txt", ".svg", ".png", ".jpg", ".jpeg", ".webp", ".pdf"}
SHA256 = re.compile(r"^[0-9a-f]{64}$")
GIT_SHA = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$")


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def _safe_relative_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("package paths must be non-empty POSIX relative paths")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe package path: {value!r}")
    if path.as_posix() != value:
        raise ValueError(f"package path must be normalized: {value!r}")
    if path.suffix.lower() not in ALLOWED_SUFFIXES:
        raise ValueError(f"unsupported package file type: {value!r}")
    return value


def _safe_package_path(value: str) -> str:
    if not isinstance(value, str) or not value or "\\" in value:
        raise ValueError("package_path must be a normalized POSIX relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or path.as_posix() != value or any(part in ("", ".", "..") for part in path.parts):
        raise ValueError(f"unsafe package_path: {value!r}")
    return value


def package_digest(source_ref: str, package_id: str, package_path: str,
                   files: list[dict], package_author: str = "") -> str:
    if not GIT_SHA.fullmatch(source_ref or ""):
        raise ValueError("source_ref must be an immutable Git commit SHA")
    if not isinstance(package_id, str) or not package_id.strip():
        raise ValueError("package_id must be non-empty")
    package_path = _safe_package_path(package_path)
    normalized = []
    seen = set()
    for entry in files:
        path = _safe_relative_path(entry.get("path"))
        digest = entry.get("sha256")
        if not isinstance(digest, str) or not SHA256.fullmatch(digest):
            raise ValueError(f"malformed SHA-256 for {path}")
        if path in seen:
            raise ValueError(f"duplicate package path: {path}")
        seen.add(path)
        normalized.append({"path": path, "sha256": digest})
    if not normalized:
        raise ValueError("package inventory must contain at least one file")
    normalized.sort(key=lambda row: row["path"])
    body = {
        "schema": SCHEMA,
        "source_ref": source_ref,
        "package_id": package_id,
        "package_path": package_path,
        "package_author": package_author,
        "files": normalized,
    }
    return sha256_bytes(canonical_bytes(body))


def build_manifest(*, source_ref: str, package_id: str, package_path: str,
                   root: str | Path, files: list[str],
                   package_author: str = "",
                   excluded_paths: list[str] | None = None) -> dict:
    base = Path(root).resolve()
    package_path = _safe_package_path(package_path)
    excluded = {_safe_relative_path(path) for path in (excluded_paths or [])}
    if not isinstance(package_author, str) or not package_author.strip():
        raise ValueError("package_author must be non-empty")
    inventory = []
    for raw in files:
        rel = _safe_relative_path(raw)
        if rel in excluded:
            raise ValueError(f"manifest inventory includes explicitly excluded path: {rel}")
        target = base / rel
        cursor = base
        for part in PurePosixPath(rel).parts:
            cursor = cursor / part
            if cursor.is_symlink():
                raise ValueError(f"symlink package entries are unsupported: {rel}")
        resolved = target.resolve()
        if base not in resolved.parents or not resolved.is_file():
            raise ValueError(f"package file is missing or outside root: {rel}")
        inventory.append({"path": rel, "sha256": sha256_bytes(resolved.read_bytes())})
    digest = package_digest(source_ref, package_id, package_path, inventory, package_author)
    return {
        "schema": SCHEMA,
        "source_ref": source_ref,
        "package_id": package_id,
        "package_path": package_path,
        "package_author": package_author,
        "excluded_paths": sorted(excluded),
        "files": sorted(inventory, key=lambda row: row["path"]),
        "package_digest": digest,
    }


def validate_manifest(manifest: dict) -> list[str]:
    errors = []
    if not isinstance(manifest, dict) or manifest.get("schema") != SCHEMA:
        return ["unsupported proposal package manifest schema"]
    try:
        actual = package_digest(manifest.get("source_ref"), manifest.get("package_id"),
                                manifest.get("package_path"), manifest.get("files", []), manifest.get("package_author", ""))
        if actual != manifest.get("package_digest"):
            errors.append("package digest mismatch")
    except (TypeError, ValueError, AttributeError) as exc:
        errors.append(str(exc))
    excluded = manifest.get("excluded_paths", [])
    if not isinstance(excluded, list) or any(not isinstance(p, str) for p in excluded):
        errors.append("excluded_paths must be an array of paths")
    else:
        try:
            normalized_excluded = {_safe_relative_path(path) for path in excluded}
            if len(normalized_excluded) != len(excluded):
                errors.append("excluded_paths contains duplicates")
            if normalized_excluded & {row.get("path") for row in manifest.get("files", []) if isinstance(row, dict)}:
                errors.append("manifest inventory overlaps explicitly excluded paths")
        except ValueError as exc:
            errors.append(str(exc))
    return errors


def verify_files(manifest: dict, root: str | Path,
                 checkout_sha: str | None = None) -> list[str]:
    errors = validate_manifest(manifest)
    if checkout_sha is not None and (
            not GIT_SHA.fullmatch(checkout_sha)
            or checkout_sha != manifest.get("source_ref")):
        errors.append("checked-out source SHA does not match immutable package ref")
    if errors:
        return errors
    base = Path(root).resolve()
    for row in manifest["files"]:
        rel = row["path"]
        try:
            _safe_relative_path(rel)
            target = base / rel
            cursor = base
            for part in PurePosixPath(rel).parts:
                cursor = cursor / part
                if cursor.is_symlink():
                    raise ValueError("symlink package entries are unsupported")
            resolved = target.resolve()
            if base not in resolved.parents or not resolved.is_file():
                raise ValueError("file is missing or outside package root")
            if sha256_bytes(resolved.read_bytes()) != row["sha256"]:
                raise ValueError("file hash mismatch")
        except (OSError, ValueError) as exc:
            errors.append(f"{rel}: {exc}")
    return errors


def verify_award(*, manifest: dict, award: dict, package_author: str,
                 reviewer: str) -> dict:
    errors = validate_manifest(manifest)
    package_author = manifest.get("package_author", "") if isinstance(manifest, dict) else ""
    if not isinstance(award, dict):
        errors.append("award payload is missing")
    else:
        manifest_digest = manifest.get("package_digest") if isinstance(manifest, dict) else None
        if award.get("package_digest") != manifest_digest:
            errors.append("award package digest does not match current package")
        if not award.get("reviewer_login") or str(award.get("reviewer_login")).casefold() != str(reviewer).casefold():
            errors.append("award reviewer identity does not match authenticated reviewer")
        if award.get("decision") not in ("shadow", "parked"):
            errors.append("award decision is not an accepted terminal disposition")
        if not award.get("ledger_ref"):
            errors.append("award ledger reference is missing")
    if not package_author or not reviewer or package_author.casefold() == reviewer.casefold():
        errors.append("independent reviewer identity is required")
    return {
        "schema": "delphi-package-consumer-verification/v1",
        "disposition": "VERIFIED" if not errors else "HELD",
        "package_digest": manifest.get("package_digest") if isinstance(manifest, dict) else None,
        "errors": errors,
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Verify Delphi proposal package and QDesk award binding")
    parser.add_argument("--manifest")
    parser.add_argument("--build", action="store_true", help="build a manifest from local package files")
    parser.add_argument("--source-ref")
    parser.add_argument("--package-id")
    parser.add_argument("--package-path")
    parser.add_argument("--package-author", default="")
    parser.add_argument("--file", action="append", default=[])
    parser.add_argument("--exclude", action="append", default=[])
    parser.add_argument("--root", required=True)
    parser.add_argument("--checkout-sha")
    parser.add_argument("--award")
    parser.add_argument("--reviewer", default="")
    parser.add_argument("--out")
    args = parser.parse_args(argv)
    if args.build:
        if not all((args.source_ref, args.package_id, args.package_path)) or not args.file:
            parser.error("--build requires --source-ref, --package-id, --package-path and at least one --file")
        manifest = build_manifest(
            source_ref=args.source_ref, package_id=args.package_id,
            package_path=args.package_path, root=args.root, files=args.file,
            package_author=args.package_author, excluded_paths=args.exclude,
        )
        output = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
        if args.out:
            Path(args.out).write_text(output, encoding="utf-8")
        print(output, end="")
        return 0
    if not args.manifest:
        parser.error("supply --manifest or --build")
    if not args.checkout_sha:
        parser.error("--checkout-sha is required for immutable consumer verification")
    manifest = json.loads(Path(args.manifest).read_text(encoding="utf-8"))
    errors = verify_files(manifest, args.root, checkout_sha=args.checkout_sha)
    if args.award:
        award = json.loads(Path(args.award).read_text(encoding="utf-8"))
        result = verify_award(manifest=manifest, award=award,
                              package_author=args.package_author, reviewer=args.reviewer)
        result["errors"] = errors + result["errors"]
        if result["errors"]:
            result["disposition"] = "HELD"
    else:
        result = {"schema": "delphi-package-consumer-verification/v1",
                  "disposition": "VERIFIED" if not errors else "HELD",
                  "package_digest": manifest.get("package_digest"),
                  "errors": errors}
    output = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.out:
        Path(args.out).write_text(output, encoding="utf-8")
    print(output, end="")
    return 0 if result["disposition"] == "VERIFIED" else 2


if __name__ == "__main__":
    raise SystemExit(main())
