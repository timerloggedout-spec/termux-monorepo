"""Hash-chain blackbox log — every plan and verdict is chained."""
from __future__ import annotations

import hashlib
import json
import time


class BlackBox:
    def __init__(self) -> None:
        self.records: list[dict] = []
        self._prev = "GENESIS"

    def log(self, event: str, detail: dict) -> dict:
        payload = {"t": round(time.time(), 3), "event": event, "detail": detail,
                   "prev": self._prev}
        digest = hashlib.sha256(
            json.dumps(payload, sort_keys=True).encode()).hexdigest()
        record = {**payload, "sha256": digest}
        self.records.append(record)
        self._prev = digest
        return record

    def verify(self) -> bool:
        prev = "GENESIS"
        for r in self.records:
            if r["prev"] != prev:
                return False
            body = {k: r[k] for k in ("t", "event", "detail", "prev")}
            if hashlib.sha256(json.dumps(body, sort_keys=True).encode()
                              ).hexdigest() != r["sha256"]:
                return False
            prev = r["sha256"]
        return True
