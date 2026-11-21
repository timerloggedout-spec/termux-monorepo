#!/usr/bin/env python3
"""Safe JSON <-> TOON adapter and deterministic comparison harness.

JSON remains canonical in repositories and machine-readable records. This
module delegates TOON syntax to the official @toon-format/cli executable;
it deliberately does not implement a second TOON parser or grammar.
"""
from __future__ import annotations
import argparse
import json
import math
import os
from pathlib import Path
import shutil
import subprocess
import sys
import time
from typing import Any

SCHEMA = "json-toon-comparison/v1"
CLI_TIMEOUT_SECONDS = 60

class InteropError(RuntimeError):
    pass

def _strict_json_loads(text: str) -> Any:
    def reject_constant(value: str) -> None:
        raise ValueError(f"non-JSON numeric constant: {value}")
    def reject_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError(f"duplicate JSON object key: {key}")
            result[key] = value
        return result
    value = json.loads(
        text, parse_constant=reject_constant, object_pairs_hook=reject_duplicate_keys
    )
    def reject_non_finite(node: Any) -> None:
        if isinstance(node, float) and not math.isfinite(node):
            raise ValueError("JSON number is outside the supported finite numeric range")
        if isinstance(node, dict):
            for child in node.values():
                reject_non_finite(child)
        elif isinstance(node, list):
            for child in node:
                reject_non_finite(child)
    reject_non_finite(value)
    return value

def _json_equal(left: Any, right: Any) -> bool:
    """Compare JSON values structurally; object order is irrelevant."""
    if isinstance(left, bool) or isinstance(right, bool):
        return type(left) is type(right) and left == right
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return left == right
    if type(left) is not type(right):
        return False
    if isinstance(left, dict):
        return left.keys() == right.keys() and all(
            _json_equal(left[key], right[key]) for key in left
        )
    if isinstance(left, list):
        return len(left) == len(right) and all(
            _json_equal(a, b) for a, b in zip(left, right)
        )
    return left == right

def _resolve_toon(executable: str | None) -> str:
    candidate = executable or os.environ.get("TOON_BIN") or "toon"
    resolved = shutil.which(candidate)
    if resolved:
        return resolved
    if Path(candidate).is_file():
        return str(Path(candidate).resolve())
    raise InteropError(
        "TOON CLI not found. Install the official @toon-format/cli package "
        "or set TOON_BIN; this adapter never downloads or executes packages."
    )

def _run_toon(binary: str, mode: str, payload: str) -> str:
    if mode not in {"encode", "decode"}:
        raise InteropError(f"unsupported TOON operation: {mode}")
    flag = "--encode" if mode == "encode" else "--decode"
    try:
        result = subprocess.run(
            [binary, flag],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
            timeout=CLI_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise InteropError(
            f"TOON CLI exceeded {CLI_TIMEOUT_SECONDS}s timeout"
        ) from exc
    if result.returncode != 0:
        detail = result.stderr.strip() or f"toon exited {result.returncode}"
        raise InteropError(detail)
    return result.stdout

def _read_input(path: str | None) -> str:
    if path and path != "-":
        return Path(path).read_text(encoding="utf-8")
    return sys.stdin.read()

def _write_output(path: str | None, value: str) -> None:
    if path and path != "-":
        Path(path).write_text(value, encoding="utf-8")
    else:
        sys.stdout.write(value)
        if value and not value.endswith("\n"):
            sys.stdout.write("\n")

def _token_counts(values: dict[str, str]) -> dict[str, Any]:
    try:
        import tiktoken  # type: ignore[import-not-found]
    except ImportError:
        return {"available": False, "reason": "tiktoken is not installed", "encodings": None}
    encodings: dict[str, Any] = {}
    for name in ("o200k_base", "cl100k_base"):
        try:
            encoder = tiktoken.get_encoding(name)
        except Exception as exc:
            encodings[name] = {"error": str(exc)}
            continue
        encodings[name] = {key: len(encoder.encode(text)) for key, text in values.items()}
    return {
        "available": True,
        "tiktoken_version": getattr(tiktoken, "__version__", None),
        "encodings": encodings,
    }

def compare_json_to_toon(json_text: str, binary: str) -> dict[str, Any]:
    source = _strict_json_loads(json_text)
    started = time.perf_counter()
    toon_text = _run_toon(binary, "encode", json_text)
    decoded_text = _run_toon(binary, "decode", toon_text)
    runtime_ms = round((time.perf_counter() - started) * 1000, 3)
    decoded = _strict_json_loads(decoded_text)
    equal = _json_equal(source, decoded)
    pretty = json.dumps(source, ensure_ascii=False, indent=2, allow_nan=False)
    compact = json.dumps(source, ensure_ascii=False, separators=(",", ":"), allow_nan=False)
    token_counts = _token_counts({
        "json_pretty": pretty, "json_compact": compact, "toon": toon_text.rstrip("\n")
    })
    return {
        "schema": SCHEMA,
        "source_format": "json",
        "candidate_format": "toon",
        "canonical_format": "json",
        "round_trip_equal": equal,
        "round_trip_status": "PASS" if equal else "FAIL",
        "runtime_ms_encode_decode": runtime_ms,
        "implementation": {
            "cli": "official @toon-format/cli",
            "version": os.environ.get("TOON_IMPLEMENTATION_VERSION"),
            "spec_version": os.environ.get("TOON_SPEC_VERSION"),
        },
        "sizes": {
            "json_pretty_chars": len(pretty),
            "json_compact_chars": len(compact),
            "toon_chars": len(toon_text.rstrip("\n")),
            "json_pretty_utf8_bytes": len(pretty.encode("utf-8")),
            "json_compact_utf8_bytes": len(compact.encode("utf-8")),
            "toon_utf8_bytes": len(toon_text.rstrip("\n").encode("utf-8")),
        },
        "tokens": token_counts,
        "policy": {
            "json_remains_canonical": True,
            "toon_is_optional_transport": True,
            "round_trip_required_for_adoption": True,
            "token_savings_are_not_quality_evidence": True,
        },
    }

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--toon-bin", help="path/name of an installed official toon CLI")
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("encode", "decode", "compare"):
        child = sub.add_parser(name)
        child.add_argument("input", nargs="?", default="-", help="input file or - for stdin")
        child.add_argument("-o", "--output", default="-", help="output file or - for stdout")
    return parser

def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = _read_input(args.input)
        binary = _resolve_toon(args.toon_bin)
        if args.command == "encode":
            _strict_json_loads(payload)
            output = _run_toon(binary, "encode", payload)
        elif args.command == "decode":
            decoded = _strict_json_loads(_run_toon(binary, "decode", payload))
            output = json.dumps(decoded, ensure_ascii=False, indent=2, allow_nan=False)
        else:
            report = compare_json_to_toon(payload, binary)
            output = json.dumps(report, ensure_ascii=False, indent=2, allow_nan=False)
            if not report["round_trip_equal"]:
                _write_output(args.output, output)
                return 1
        _write_output(args.output, output)
        return 0
    except (OSError, ValueError, InteropError) as exc:
        print(f"toon-interop: {exc}", file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())
