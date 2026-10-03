"""Optional Rust hot-path adapter for Context Relationship collection.

The Python implementation remains authoritative. This module only delegates bounded
fingerprinting/cost analysis when a compiled accelerator is explicitly available.
""" 

from __future__ import annotations

import json
import os
import subprocess
from pathlib import Path
from typing import Any, Iterable, Mapping

DEFAULT_BINARY = Path(__file__).with_name("rust_accel") / "target" / "release" / "crg-rust-accel"


class RustAccelerationError(RuntimeError):
    """The optional accelerator was requested but could not complete safely."""


def _enabled() -> bool:
    return os.environ.get("CRG_RUST_ACCEL", "auto").strip().lower() not in {"0", "false", "off", "no"}


def _binary() -> Path:
    configured = os.environ.get("CRG_RUST_ACCEL_BIN")
    return Path(configured).expanduser() if configured else DEFAULT_BINARY


def analyze_fragments(fragments: Iterable[Mapping[str, Any]]) -> dict[str, Any] | None:
    """Run the accelerator once for a bounded batch; return None when unavailable."""
    if not _enabled():
        return None

    binary = _binary()
    if not binary.is_file():
        if os.environ.get("CRG_RUST_ACCEL", "auto").strip().lower() in {"required", "require", "1", "true", "on"}:
            raise RustAccelerationError(f"Rust accelerator is required but missing: {binary}")
        return None

    payload = "".join(json.dumps(dict(item), separators=(",", ":"), ensure_ascii=False) + "\n" for item in fragments)
    try:
        completed = subprocess.run(
            [str(binary)],
            input=payload,
            text=True,
            capture_output=True,
            check=False,
            timeout=float(os.environ.get("CRG_RUST_ACCEL_TIMEOUT", "30")),
        )
    except (OSError, subprocess.SubprocessError) as exc:
        raise RustAccelerationError(f"Rust accelerator invocation failed: {exc}") from exc

    if completed.returncode != 0:
        raise RustAccelerationError(
            f"Rust accelerator exited {completed.returncode}: {completed.stderr.strip()[:500]}"
        )
    try:
        result = json.loads(completed.stdout)
    except json.JSONDecodeError as exc:
        raise RustAccelerationError("Rust accelerator returned invalid JSON") from exc
    if not isinstance(result, dict) or not isinstance(result.get("fingerprints"), list):
        raise RustAccelerationError("Rust accelerator returned an invalid analysis contract")
    return result
