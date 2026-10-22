#!/usr/bin/env python3
"""Passively archive stdin verbatim and derive an allowlisted three-line view.

Never launches a producer. Raw diagnostics are private and must not be published.
"""
import argparse
import json
import os
from pathlib import Path
import shutil
import sys

from telemetry import MAX_EVENT_BYTES, normalize, steering


def private_file(path):
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    return os.fdopen(os.open(path, flags, 0o600), "wb")


def captured_lines(source, raw):
    """Archive every byte; bound each parse candidate independently of line size."""
    pending = bytearray()
    oversized = False
    read = getattr(source, "read1", source.read)
    while True:
        chunk = read(65536)
        if not chunk:
            break
        raw.write(chunk)
        raw.flush()
        parts = chunk.split(b"\n")
        for index, part in enumerate(parts):
            if not oversized:
                if len(pending) + len(part) > MAX_EVENT_BYTES:
                    pending.clear()
                    oversized = True
                else:
                    pending.extend(part)
            if index < len(parts) - 1:
                if oversized:
                    yield "INVALID_OVERSIZED_EVENT"
                else:
                    try:
                        yield pending.decode("utf-8", errors="strict")
                    except UnicodeDecodeError:
                        yield "INVALID_UTF8_EVENT"
                pending.clear()
                oversized = False
    if pending or oversized:
        if oversized:
            yield "INVALID_OVERSIZED_EVENT"
        else:
            try:
                yield pending.decode("utf-8", errors="strict")
            except UnicodeDecodeError:
                yield "INVALID_UTF8_EVENT"


def capture(source, destination, *, diagnostics=None, model=None, quota=None,
            run_id=None, account_scope=None):
    """Create a new private directory; never overwrite a prior capture."""
    destination = Path(destination)
    destination.mkdir(mode=0o700)
    os.chmod(destination, 0o700)
    with private_file(destination / "stream.ndjson") as raw:
        record = normalize(captured_lines(source, raw), model, quota, run_id, account_scope)
    if diagnostics is not None:
        with open(diagnostics, "rb") as source_stderr:
            with private_file(destination / "diagnostics.stderr") as target_stderr:
                shutil.copyfileobj(source_stderr, target_stderr, length=65536)
    return write_outputs(record, destination)


def write_outputs(record, destination):
    """Write allowlisted metadata and steering after capture/process completion."""
    with private_file(destination / "record.json") as output:
        output.write((json.dumps(record, allow_nan=False) + "\n").encode("utf-8"))
    summary = steering(record) + "\n"
    with private_file(destination / "steering.txt") as output:
        output.write(summary.encode("utf-8"))
    return record, summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", required=True, help="New private run directory; must not exist")
    parser.add_argument("--diagnostics", help="Existing producer stderr file to preserve verbatim")
    parser.add_argument("--model", help="Explicit observed model, never a guessed default")
    parser.add_argument("--run-id")
    parser.add_argument("--account-scope", help="Non-secret account alias")
    parser.add_argument("--quota", help="Optional manual /usage observation JSON")
    args = parser.parse_args()
    quota = None
    if args.quota:
        try:
            with open(args.quota, "rb") as source:
                data = source.read(MAX_EVENT_BYTES + 1)
            if len(data) > MAX_EVENT_BYTES:
                raise ValueError("quota observation exceeds size limit")
            quota = json.loads(data, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
        except (OSError, ValueError, UnicodeDecodeError, RecursionError) as error:
            print(f"Invalid quota observation: {error}", file=sys.stderr)
            return 64
        if not isinstance(quota, dict):
            print("Invalid quota observation: expected a JSON object", file=sys.stderr)
            return 64
    try:
        record, summary = capture(sys.stdin.buffer, args.capture_dir,
                                  diagnostics=args.diagnostics, model=args.model,
                                  quota=quota, run_id=args.run_id,
                                  account_scope=args.account_scope)
    except OSError as error:
        print(f"Capture failed: {error.__class__.__name__}; inspect private capture locally", file=sys.stderr)
        return 3
    sys.stdout.write(summary)
    # This is filter completion, not evidence that the producer process succeeded.
    return 2 if record["status"] == "INCOMPLETE" else 0


if __name__ == "__main__":
    sys.exit(main())
