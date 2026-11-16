"""Validation for measured edge inference records."""

from __future__ import annotations

from typing import Any, Mapping


REQUIRED_IDENTITY = {
    "device", "soc", "ram", "os_version", "runtime", "runtime_version",
    "model_digest", "quantization", "backend", "accelerator", "workload_fixture",
}

REQUIRED_MEASUREMENTS = {
    "tokens_per_second", "peak_rss_bytes", "wall_time_ms", "failure_class",
}


def validate_run(record: Mapping[str, Any]) -> list[str]:
    errors = []
    for key in sorted(REQUIRED_IDENTITY):
        if not record.get(key):
            errors.append(f"missing identity: {key}")
    for key in sorted(REQUIRED_MEASUREMENTS):
        if key not in record:
            errors.append(f"missing measurement: {key}")
    if record.get("energy_mwh") is not None and record.get("energy_method") is None:
        errors.append("energy_mwh requires energy_method")
    if record.get("target") and record["target"] not in {
        "arm64-linux", "x86_64-linux", "android", "termux", "offline"
    }:
        errors.append("unsupported target")
    return errors
