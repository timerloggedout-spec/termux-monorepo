#!/usr/bin/env python3
"""MSM-002 — append-only performance ledger (bounded metadata only)."""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

REQUIRED_DIMS = (
    "correctness_gate_pass",
    "substantive_review_resolution",
    "duplicate_noise_avoidance",
    "time_to_safe_feedback",
    "cooldown_queue_efficiency",
    "resource_cost",
    "coordinated_async_completion",
)


@dataclass
class LedgerSample:
    role: str
    model_id: str
    mode: str = "series"
    dimensions: dict[str, Any] = field(default_factory=dict)
    head_sha: str | None = None
    evidence_source: str = "observe"
    observed_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def sample_id(self) -> str:
        payload = f"{self.role}|{self.model_id}|{self.observed_at}|{self.head_sha or ''}"
        return hashlib.sha256(payload.encode()).hexdigest()[:16]

    def confidence(self, n: int) -> float:
        if n <= 0:
            return 0.0
        if n < 3:
            return 0.2  # historic / insufficient band
        return min(1.0, 0.2 + 0.1 * n)

    def to_record(self, n_prior: int = 0) -> dict[str, Any]:
        dims = {k: self.dimensions.get(k) for k in REQUIRED_DIMS}
        return {
            "sample_id": self.sample_id(),
            "observed_at": self.observed_at,
            "head_sha": self.head_sha,
            "role": self.role,
            "model_id": self.model_id,
            "mode": self.mode,
            "dimensions": dims,
            "provenance": {
                "evidence_source": self.evidence_source,
                "decision_schema_version": "msm-ledger-1",
            },
            "confidence": self.confidence(n_prior),
        }


class PerformanceLedger:
    """In-memory + optional JSONL path. Never stores raw PR/issue bodies."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = path
        self._samples: list[dict[str, Any]] = []
        if path and path.is_file():
            for line in path.read_text(encoding="utf-8").splitlines():
                line = line.strip()
                if line:
                    self._samples.append(json.loads(line))

    def _n_for(self, role: str, model_id: str) -> int:
        return sum(1 for s in self._samples if s.get("role") == role and s.get("model_id") == model_id)

    def append(self, sample: LedgerSample) -> dict[str, Any]:
        n = self._n_for(sample.role, sample.model_id)
        rec = sample.to_record(n_prior=n)
        self._samples.append(rec)
        if self.path:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            with self.path.open("a", encoding="utf-8") as f:
                f.write(json.dumps(rec, sort_keys=True) + "\n")
        return rec

    def aggregate(self, role: str | None = None) -> dict[str, Any]:
        buckets: dict[tuple[str, str], list[dict[str, Any]]] = {}
        for s in self._samples:
            key = (s["role"], s["model_id"])
            if role and s["role"] != role:
                continue
            buckets.setdefault(key, []).append(s)
        out: dict[str, Any] = {}
        for (r, mid), rows in buckets.items():
            out.setdefault(r, {})[mid] = {
                "n": len(rows),
                "confidence": rows[-1].get("confidence", 0.0),
                "last_sample_id": rows[-1].get("sample_id"),
                # weight stays 1.0 until promote rule (observe cycles + ledger decision)
                "weight": 1.0,
                "weight_policy": "observe_only_until_promote",
            }
        return {"schema_version": 1, "aggregates": out, "sample_count": len(self._samples)}


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--demo", action="store_true")
    p.add_argument("--path", type=Path, default=None)
    args = p.parse_args()
    led = PerformanceLedger(args.path)
    if args.demo:
        led.append(
            LedgerSample(
                role="triage",
                model_id="stealth/ox-alpha",
                mode="series",
                dimensions={"correctness_gate_pass": True, "resource_cost": 1},
            )
        )
    print(json.dumps(led.aggregate(), indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
