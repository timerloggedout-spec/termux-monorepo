#!/usr/bin/env python3
"""Emit a privacy-preserving Hex/Moneyball evidence envelope from NDJSON events.

This adapter intentionally does not invent missing run/task/provider metrics.
It preserves only stable metadata that can be supported by the source events and
hashes free-form messages instead of exporting their contents.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

CONTRACT = "3l0.moneyball.v1"


def sha256_text(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def sanitize(event: dict[str, Any]) -> dict[str, Any]:
    message = event.get("message")
    out = {
        "contract_version": CONTRACT,
        "timestamp": event.get("timestamp"),
        "level": event.get("level"),
        "agent_id": event.get("agent"),
        "target": event.get("target"),
        "attempt_no": event.get("attempt"),
    }
    if isinstance(message, str):
        out["message_sha256"] = sha256_text(message)
        out["message_present"] = True
    else:
        out["message_present"] = False
    return {k: v for k, v in out.items() if v is not None}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("input", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()

    count = 0
    with args.input.open("r", encoding="utf-8") as src, args.output.open("w", encoding="utf-8") as dst:
        for line in src:
            if not line.strip():
                continue
            event = json.loads(line)
            dst.write(json.dumps(sanitize(event), separators=(",", ":")) + "\n")
            count += 1

    print(json.dumps({"contract_version": CONTRACT, "records": count, "output": str(args.output)}))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
