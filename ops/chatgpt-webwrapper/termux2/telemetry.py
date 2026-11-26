#!/usr/bin/env python3
"""ChatGPT webWrapper — telemetry listener (driver layer). TERMUX bundle copy:
ACTOR defaults to "termux-device" (WEBWRAPPER_ACTOR overrides); event
names and record shape are identical to the VM instance's telemetry.py.

Per the stack model (DeepAgent.py -> core.py), the entrypoint layer carries
a LISTENER that exports telemetry as the run happens — not an after-the-fact
summary. Events append to a local JSONL stream in the work dir, shaped for
Provenance ingestion (the #5555 ChatGPT leg): one self-describing event per
line {ts, stream, actor, event, ...}.

Separate artifact from the harvest manifest: manifest = checkpoint state,
telemetry = the exportable event record.
"""
import json
import os
from datetime import datetime, timezone

BASE = os.path.dirname(os.path.abspath(__file__))
STREAM = os.path.join(BASE, "telemetry.jsonl")
ACTOR = os.environ.get("WEBWRAPPER_ACTOR", "termux-device")
SOURCE = "chatgpt-webwrapper"


def emit(event, **fields):
    rec = {
        "ts": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "stream": SOURCE,
        "actor": ACTOR,
        "event": event,
    }
    rec.update(fields)
    with open(STREAM, "a") as f:
        f.write(json.dumps(rec) + "\n")
        f.flush()
    return rec
