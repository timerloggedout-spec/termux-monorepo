#!/usr/bin/env python3
"""dispatch_pipeline.py — event-sourced dispatch pipeline (local form).
TERMUX bundle copy: the session-cache loader reads core_se (the device
instance's core) instead of core; everything else is identical.

Conformance: archwiz/dispatch_pipeline.py (termux-monorepo master).
Decouples session ingestion from downstream updates: core.py's cache-save
hook calls update_all(session_id) after every session-store save (the
model's hook shape, deepcli/deepcli/core.py), and the fan-out runs every
registered dispatcher with (session_id, messages), each isolated so one
crashing dispatcher never blocks the others or the save.

Default dispatcher: telemetry export (telemetry_export.dispatch_telemetry)
— the entrypoint listener's telemetry leg in record form. Further
dispatchers register with pipeline.register(func).
"""
import json
import logging
import os
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent
LOG_FILE = BASE / "dispatch.log"

logging.basicConfig(
    filename=str(LOG_FILE),
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)
logger = logging.getLogger("dispatch")


class DispatchPipeline:
    def __init__(self):
        self.dispatchers = []
        self._register_default_dispatchers()

    def register(self, func):
        self.dispatchers.append(func)

    def _register_default_dispatchers(self):
        self.register(self.dispatch_telemetry)

    def dispatch_telemetry(self, session_id, messages):
        """Export the session's records (provenance + session-history +
        pointers) via telemetry_export."""
        try:
            sys.path.insert(0, str(BASE))
            import telemetry_export

            result = telemetry_export.dispatch_telemetry(session_id, messages)
            logger.info(f"Telemetry export for {session_id}: {result}")
        except Exception as e:
            logger.error(f"Telemetry dispatch failed for {session_id}: {e}")

    def run(self, session_id, messages):
        """Execute all registered dispatchers."""
        start_time = time.time()
        logger.info(f"Starting dispatch for session {session_id} ({len(messages)} messages)")

        for dispatcher in self.dispatchers:
            try:
                dispatcher(session_id, messages)
            except Exception as e:
                logger.error(f"Dispatcher {dispatcher.__name__} crashed: {e}")

        duration = time.time() - start_time
        logger.info(f"Dispatch completed for {session_id} in {duration:.2f}s")


def _load_messages(session_id):
    sys.path.insert(0, str(BASE))
    import core_se as core

    return core.load_session_cache(session_id) or []


def update_all(session_id):
    """Entry point for core.py's save hook (the model's call shape):
    load the session's messages from the session store and fan out."""
    messages = _load_messages(session_id)
    pipeline = DispatchPipeline()
    pipeline.run(session_id, messages)


def trigger_dispatch(session_id, messages):
    """Entry point for ingestors holding messages in hand."""
    pipeline = DispatchPipeline()
    pipeline.run(session_id, messages)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: dispatch_pipeline.py <session_id> [path_to_json]")
        sys.exit(1)

    sid = sys.argv[1]
    msgs = []

    if len(sys.argv) > 2:
        p = Path(sys.argv[2])
        if p.exists():
            msgs = json.loads(p.read_text())

    trigger_dispatch(sid, msgs)
