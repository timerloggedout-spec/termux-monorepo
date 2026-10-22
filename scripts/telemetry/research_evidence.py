#!/usr/bin/env python3
"""Project bounded execution telemetry into the existing observe-only 3L0 ledger."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from scripts.model_selection_market.ledger import LedgerSample, PerformanceLedger, REQUIRED_DIMS
from src.telemetry import sanitize_correlation

TERMINAL = {"response", "error", "denied", "cancelled", "completed", "failed",
            "admission_denied", "execution_complete", "execution_failed", "execution_cancelled"}


class ExecutionSample(LedgerSample):
    """Existing sample schema, with bounded provenance and no quality claim."""
    def __init__(self, correlation):
        self.correlation = correlation
        model = correlation.get("model", "UNKNOWN")
        provider = correlation.get("provider")
        if provider and not model.startswith(provider + "/"):
            model = provider + "/" + model
        super().__init__(role=correlation.get("adapter", "UNKNOWN"), model_id=model,
                         mode="series", dimensions={key: None for key in REQUIRED_DIMS},
                         evidence_source="termux_telemetry")

    def sample_id(self):
        identity = {key: self.correlation.get(key) for key in
                    ("run_id", "job_id", "request_id", "attempt_id", "adapter", "provider", "model")}
        return hashlib.sha256(json.dumps(identity, sort_keys=True).encode()).hexdigest()[:32]

    def confidence(self, n):
        # Even a million HTTP completions do not establish task correctness.
        return 0.0

    def to_record(self, n_prior=0):
        record = super().to_record(n_prior=n_prior)
        record["provenance"]["execution"] = self.correlation
        record["provenance"]["task_outcome"] = "UNKNOWN"
        return record


def ingest(path: Path, ledger_path: Path | None = None) -> list[dict]:
    """Ingest one terminal observation per attempt; no scorer or routing mutation.

    The caller owns serialization of writes to the existing performance ledger.
    Repeated ingestion and both adapter/hub terminal events cannot inflate samples.
    """
    ledger = PerformanceLedger(ledger_path)
    seen = {sample.get("sample_id") for sample in ledger._samples}
    records = []
    if path.is_symlink():
        raise ValueError("telemetry input must not be a symlink")
    with path.open("rb") as source:
        while True:
            line = source.readline(8193)
            if not line:
                break
            if len(line) > 8192:
                raise ValueError("telemetry event exceeds bounded ingestion contract")
            try:
                event = json.loads(line)
            except (ValueError, TypeError):
                continue
            corr = sanitize_correlation(event.get("correlation")) if isinstance(event, dict) else {}
            if corr.get("event") not in TERMINAL or "outcome" not in corr:
                continue
            if not all(corr.get(key) for key in ("run_id", "job_id", "request_id", "attempt_id", "adapter", "model")):
                continue
            sample = ExecutionSample(corr)
            if sample.sample_id() in seen:
                continue
            records.append(ledger.append(sample))
            seen.add(sample.sample_id())
    return records


def main(argv=None) -> int:
    import argparse
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("telemetry", type=Path)
    parser.add_argument("--ledger", type=Path)
    args = parser.parse_args(argv)
    print(json.dumps(ingest(args.telemetry, args.ledger), sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
