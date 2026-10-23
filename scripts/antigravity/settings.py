#!/usr/bin/env python3
"""Prepare a verified, private candidate for the requested Antigravity settings change."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import stat
import sys
from typing import Any

MAX_BYTES = 1024 * 1024
_REQUIRED = {
    "toolPermission": "always-proceed",
    "artifactReviewPolicy": "agent-decides",
}


class SettingsError(ValueError):
    """Input settings are invalid or do not meet the required policy."""


def _reject_constant(value: str) -> None:
    raise SettingsError(f"non-finite JSON number is not allowed: {value}")


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise SettingsError("duplicate JSON object key")
        result[key] = value
    return result


def _finite_float(value: str) -> float:
    result = float(value)
    if not math.isfinite(result):
        raise SettingsError("overflowing JSON number is not allowed")
    return result


def _decoder() -> json.JSONDecoder:
    return json.JSONDecoder(object_pairs_hook=_unique_object, parse_constant=_reject_constant,
                            parse_float=_finite_float)


def _scan_top_level(data: str, decoder: json.JSONDecoder) -> tuple[dict[str, Any], tuple[int, int] | None]:
    """Validate a JSON document and return its root object plus verbosity value span."""
    n = len(data)
    pos = 0
    while pos < n and data[pos].isspace():
        pos += 1
    if pos >= n or data[pos] != "{":
        raise SettingsError("JSON root must be an object")
    pos += 1
    root: dict[str, Any] = {}
    verbosity_span: tuple[int, int] | None = None
    while True:
        while pos < n and data[pos].isspace():
            pos += 1
        if pos >= n:
            raise SettingsError("incomplete JSON object")
        if data[pos] == "}":
            pos += 1
            break
        if data[pos] != '"':
            raise SettingsError("object key must be a JSON string")
        key_start = pos
        try:
            key, key_end = decoder.raw_decode(data, pos)
        except (json.JSONDecodeError, SettingsError) as exc:
            raise SettingsError("invalid JSON object key") from exc
        if not isinstance(key, str):
            raise SettingsError("object key must be a string")
        if key in root:
            raise SettingsError("duplicate JSON object key")
        pos = key_end
        while pos < n and data[pos].isspace():
            pos += 1
        if pos >= n or data[pos] != ":":
            raise SettingsError("missing colon after object key")
        pos += 1
        while pos < n and data[pos].isspace():
            pos += 1
        value_start = pos
        try:
            value, value_end = decoder.raw_decode(data, pos)
        except (json.JSONDecodeError, SettingsError) as exc:
            raise SettingsError("invalid JSON value") from exc
        if key == "verbosity":
            verbosity_span = (value_start, value_end)
        root[key] = value
        pos = value_end
        while pos < n and data[pos].isspace():
            pos += 1
        if pos < n and data[pos] == ",":
            pos += 1
            continue
        if pos < n and data[pos] == "}":
            pos += 1
            break
        raise SettingsError("expected comma or closing brace")

    while pos < n and data[pos].isspace():
        pos += 1
    if pos != n:
        raise SettingsError("trailing data after JSON document")
    # Parsing the complete document additionally checks nested structure and duplicates
    # at every depth, using the strict object_pairs_hook.
    try:
        parsed = decoder.decode(data)
    except (json.JSONDecodeError, SettingsError) as exc:
        raise SettingsError("invalid JSON document") from exc
    if not isinstance(parsed, dict):
        raise SettingsError("JSON root must be an object")
    # Both independently constructed dictionaries must match; this ensures scanner
    # acceptance and standard decoder interpretation stay aligned.
    if parsed != root:
        raise SettingsError("inconsistent JSON parsing")
    return root, verbosity_span


def prepare(raw: bytes) -> bytes:
    """Validate raw UTF-8 JSON bytes and change only top-level verbosity low to high."""
    if not isinstance(raw, bytes):
        raise TypeError("raw must be bytes")
    if len(raw) > MAX_BYTES:
        raise SettingsError("input exceeds 1 MiB limit")
    try:
        text = raw.decode("utf-8", errors="strict")
    except UnicodeDecodeError as exc:
        raise SettingsError("input must be valid UTF-8") from exc
    if text.startswith("\ufeff"):
        raise SettingsError("UTF-8 BOM is not allowed")
    decoder = _decoder()
    try:
        root, span = _scan_top_level(text, decoder)
    except (RecursionError, OverflowError) as exc:
        raise SettingsError("settings exceed safe parser limits") from exc
    if span is None:
        raise SettingsError("missing top-level verbosity")
    for key, expected in _REQUIRED.items():
        if key not in root or root[key] != expected or not isinstance(root[key], str):
            raise SettingsError("required settings policy is not satisfied")
    verbosity = root["verbosity"]
    if not isinstance(verbosity, str) or verbosity not in ("low", "high"):
        raise SettingsError("top-level verbosity must be low or high")
    if verbosity == "high":
        return raw
    start, end = span
    return (text[:start] + '"high"' + text[end:]).encode("utf-8")


def _read_limited(path: str) -> bytes:
    with open(path, "rb") as source:
        raw = source.read(MAX_BYTES + 1)
    if len(raw) > MAX_BYTES:
        raise SettingsError("input exceeds 1 MiB limit")
    return raw


def _write_exclusive(path: str, data: bytes) -> None:
    # O_NOFOLLOW disallows a symlink leaf; O_EXCL prevents overwriting an existing path.
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    flags |= getattr(os, "O_NOFOLLOW", 0)
    fd = os.open(path, flags, 0o600)
    try:
        os.fchmod(fd, 0o600)
        with os.fdopen(fd, "wb", closefd=False) as output:
            output.write(data)
            output.flush()
            os.fsync(fd)
    except BaseException:
        os.close(fd)
        try:
            os.unlink(path)
        except OSError:
            pass
        raise
    finally:
        try:
            os.close(fd)
        except OSError:
            pass


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, help="source settings JSON")
    parser.add_argument("--output", required=True, help="new private candidate path")
    args = parser.parse_args(argv)
    try:
        before = _read_limited(args.input)
        after = prepare(before)
        _write_exclusive(args.output, after)
    except (OSError, SettingsError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(f"BEFORE_SHA256={hashlib.sha256(before).hexdigest()} AFTER_SHA256={hashlib.sha256(after).hexdigest()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
