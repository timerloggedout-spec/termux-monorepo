#!/usr/bin/env python3
"""MSM-004 — DSPy DoE-MVT consideration lane stub.

Not model-router primary. Arms feed Approxination A/B/C/D + performance ledger.
No paid routes. No silent weight mutation.
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class DoeArm:
    arm_id: str  # A|B|C|D or custom
    signature: str
    metric_names: list[str] = field(default_factory=lambda: ["exact_match", "latency_ms"])
    free_only: bool = True


class DspyDoeStub:
    """Offline-capable stub: records arms + synthetic metrics for ledger/cards."""

    def __init__(self) -> None:
        self.runs: list[dict[str, Any]] = []

    def run_arm(self, arm: DoeArm, *,
                model_id: str = "stealth/ox-alpha",
                role: str = "triage") -> dict[str, Any]:
        if not arm.free_only:
            raise ValueError("MSM-004 free_only required")
        # Synthetic offline metrics — real DSPy optimizer is optional later install
        metrics = {name: (1.0 if name == "exact_match" else 12.0) for name in arm.metric_names}
        rec = {
            "lane": "dspy_doe_consideration",
            "not_default_router": True,
            "arm_id": arm.arm_id,
            "signature": arm.signature,
            "model_id": model_id,
            "role": role,
            "metrics": metrics,
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "affinity": ["approxination_ABCD", "performance_ledger"],
        }
        self.runs.append(rec)
        return rec

    def cohort_summary(self) -> dict[str, Any]:
        return {
            "policy": "consideration_only",
            "run_count": len(self.runs),
            "arms": [r["arm_id"] for r in self.runs],
            "note": "Promote optimizer artifacts only via dual-gate PR; never auto weight mutate",
        }


def main() -> int:
    import argparse

    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--demo", action="store_true")
    args = p.parse_args()
    stub = DspyDoeStub()
    if args.demo:
        for aid, sig in [("A", "triage_v1"), ("B", "triage_v2"), ("C", "triage_cot"), ("D", "triage_short")]:
            stub.run_arm(DoeArm(arm_id=aid, signature=sig))
    print(json.dumps({"runs": stub.runs, "summary": stub.cohort_summary()}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
