"""Read-only engineering executable inventory for Termux and Linux runners."""
from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from ops.engineering.taxonomy import load_taxonomy, validate  # noqa: E402


def runtime_name() -> str:
    """Return the observed runtime family."""
    prefix = os.environ.get("PREFIX", "")
    if os.environ.get("TERMUX_VERSION") or "com.termux" in prefix:
        return "termux"
    return sys.platform


def build_report(taxonomy: dict[str, Any]) -> dict[str, Any]:
    """Report local executable presence and external product classification."""
    tools = []
    for item in taxonomy.get("nodes", []):
        if item.get("kind") != "tool":
            continue

        metadata = item.get("metadata") or {}
        commands = metadata.get("probe_commands") or []
        target = metadata.get("execution_target", "unknown")

        if target.startswith("vendor-"):
            matched = None
            detection_state = "external"
            detected = None
        else:
            matched = next(
                (command for command in commands if shutil.which(command)),
                None,
            )
            detection_state = "present" if matched is not None else "absent"
            detected = matched is not None

        tools.append(
            {
                "id": item["id"],
                "name": item["name"],
                "detected": detected,
                "detection_state": detection_state,
                "matched_command": matched,
                "execution_target": target,
                "termux_runtime": metadata.get("termux_runtime", "unverified"),
                "license_class": metadata.get("license_class", "unknown"),
                "access": metadata.get("access", "unknown"),
            }
        )

    return {
        "schema": "engineering-toolchain-probe/v1",
        "observed_at": datetime.now(timezone.utc).isoformat(),
        "runtime": runtime_name(),
        "tools": tools,
        "summary": {
            "catalogued": len(tools),
            "detected": sum(
                1 for item in tools if item["detection_state"] == "present"
            ),
            "local_missing": sum(
                1 for item in tools if item["detection_state"] == "absent"
            ),
            "external": sum(
                1 for item in tools if item["detection_state"] == "external"
            ),
        },
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true", help="emit machine-readable JSON")
    args = parser.parse_args()

    taxonomy = load_taxonomy()
    errors = validate(taxonomy)
    if errors:
        print("\n".join(errors), file=sys.stderr)
        return 1

    report = build_report(taxonomy)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True))
        return 0

    summary = report["summary"]
    print(
        "Engineering tools: "
        f"{summary['detected']} detected / "
        f"{summary['local_missing']} local PATH gaps / "
        f"{summary['external']} external"
    )
    for item in report["tools"]:
        print(f"{item['id']}: {item['detection_state']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
