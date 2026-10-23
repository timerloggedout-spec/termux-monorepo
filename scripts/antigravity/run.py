#!/usr/bin/env python3
"""Run an explicitly authorized producer once; archive privately on the controller.

No default command, retries, model selection, settings changes, or quota probes.
Unlike capture.py, this entry point DOES launch the exact command after --.
"""
import argparse
import json
import os
from pathlib import Path
import signal
import subprocess
import sys

from capture import captured_lines, emit_event, private_file, write_outputs
from telemetry import MAX_EVENT_BYTES, normalize


def stop_producer(process):
    """Stop the local producer group on capture failure; never retry it."""
    if process.poll() is None:
        try:
            os.killpg(process.pid, signal.SIGTERM)
        except ProcessLookupError:
            pass
        try:
            process.wait(timeout=5)
        except subprocess.TimeoutExpired:
            try:
                os.killpg(process.pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            process.wait()


def run(command, destination, *, model=None, quota=None, run_id=None,
        account_scope=None):
    if not command:
        raise ValueError("explicit producer command required")
    destination = Path(destination)
    destination.mkdir(mode=0o700)
    os.chmod(destination, 0o700)
    # Open private destinations BEFORE launch. Stderr goes straight to disk,
    # stdout is archived verbatim, and the allowlisted event file flushes per event.
    with private_file(destination / "diagnostics.stderr") as diagnostics:
        with private_file(destination / "stream.ndjson") as raw:
            with private_file(destination / "events.ndjson") as events:
                event_sink = lambda event: emit_event(events, event)
                try:
                    process = subprocess.Popen(command, stdout=subprocess.PIPE,
                                               stderr=diagnostics, start_new_session=True)
                except OSError as error:
                    record = normalize([], model, quota, run_id, account_scope,
                                       event_sink=event_sink)
                    record["producer_exit_code"] = None
                    record["producer_launch_error"] = error.__class__.__name__
                    record, summary = write_outputs(record, destination)
                    return record, summary, 3
                try:
                    with process.stdout as source:
                        record = normalize(captured_lines(source, raw), model, quota,
                                           run_id, account_scope, event_sink=event_sink)
                    code = process.wait()
                except BaseException:
                    stop_producer(process)
                    raise
    record["producer_exit_code"] = code
    record, summary = write_outputs(record, destination)
    # Preserve real process failures, but do not turn an incomplete/failed result
    # into success just because the transport process exited zero.
    if code:
        exit_code = code if code > 0 else 128 - code
        exit_code = min(exit_code, 255)
    else:
        exit_code = 0 if record["status"] == "SUCCESS" else (
            2 if record["status"] == "INCOMPLETE" else 1)
    return record, summary, exit_code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture-dir", required=True,
                        help="New private run directory outside the repository")
    parser.add_argument("--model", help="Explicit observed model; not a producer override")
    parser.add_argument("--run-id")
    parser.add_argument("--account-scope", help="Non-secret account alias")
    parser.add_argument("--quota", help="Optional existing manual /usage observation JSON")
    # A literal separator is mandatory: flags cannot accidentally become a task.
    if "--" not in sys.argv[1:]:
        parser.error("explicit -- COMMAND required; no producer was launched")
    separator = sys.argv.index("--")
    args = parser.parse_args(sys.argv[1:separator])
    command = sys.argv[separator + 1:]
    if not command:
        parser.error("explicit -- COMMAND required; no producer was launched")
    quota = None
    if args.quota:
        try:
            with open(args.quota, "rb") as source:
                data = source.read(MAX_EVENT_BYTES + 1)
            if len(data) > MAX_EVENT_BYTES:
                raise ValueError("oversized quota")
            quota = json.loads(data, parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
            if not isinstance(quota, dict):
                raise ValueError("quota must be an object")
        except (OSError, ValueError, UnicodeDecodeError, RecursionError):
            print("Invalid existing quota observation; no producer was launched", file=sys.stderr)
            return 64
    try:
        _, summary, code = run(command, args.capture_dir, model=args.model,
                               quota=quota, run_id=args.run_id,
                               account_scope=args.account_scope)
    except KeyboardInterrupt:
        print("Capture interrupted; inspect partial private archive; do not retry automatically",
              file=sys.stderr)
        return 130
    except OSError as error:
        print(f"Capture failed: {error.__class__.__name__}; inspect private archive; no automatic retry",
              file=sys.stderr)
        return 3
    sys.stdout.write(summary)
    return code


if __name__ == "__main__":
    sys.exit(main())
