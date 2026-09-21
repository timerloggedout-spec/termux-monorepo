#!/usr/bin/env python3
"""P6: seed 17_Papers/citations JSON stubs from known operator sources.

Offline. Expand later with live arXiv/OpenAlex resolvers.
"""

from __future__ import annotations

import argparse
import json
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "refTemplates" / "17_Papers" / "citations"

SEEDS = [
    {
        "id": "laya-convai",
        "title": "Laya (ConvAI Innovations)",
        "url": "https://laya.convaiinnovations.com",
        "source_class": "seeded",
        "linked_slots": ["16_Org_Phased/laya"],
        "priority": "HIGH",
        "eval_notes": "IMPLEMENTATION phase; dense intercom required",
    },
    {
        "id": "glm-inference-infra",
        "title": "Toward Recursive Self-Improvement: How GLM Built Its Own Inference Infrastructure",
        "url": "https://z.ai/blog/glm-built-its-inference-infrastructure",
        "source_class": "seeded",
        "linked_slots": ["DENSE-FEEDBACK-INTERCOM", "Paper2Agent"],
        "priority": "HIGH",
        "eval_notes": "Dense feedback intercom seed; not Paper2Agent-only",
    },
    {
        "id": "needle-3-cactus",
        "title": "Needle 3 — foundation model for tiny devices",
        "url": "https://cactuscompute.com/needle",
        "source_class": "seeded",
        "linked_slots": ["01_Agent_Runtime", "15_Research_Repo_Templates/cactus-needle"],
        "priority": "normal",
        "eval_notes": "On-device tool call + extraction",
    },
    {
        "id": "opencode-research-papers",
        "title": "opencode-research-papers (arXiv + OpenAlex)",
        "url": "https://github.com/saim-x/opencode-research-papers",
        "source_class": "github",
        "linked_slots": ["17_Papers", "15_Research_Repo_Templates/opencode-research-papers"],
        "priority": "normal",
        "eval_notes": "Primary no-key paper scanner",
    },
    {
        "id": "openresearch-alphaxiv",
        "title": "alphaXiv OpenResearch",
        "url": "https://github.com/alphaXiv/OpenResearch",
        "source_class": "github",
        "linked_slots": ["15_Research_Repo_Templates"],
        "priority": "normal",
        "eval_notes": "Local-first research agents",
    },
]


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=OUT)
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat()
    for seed in SEEDS:
        payload = {**seed, "collected_at": now}
        path = args.output_dir / f"{seed['id']}.json"
        path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print(f"OK: {path.relative_to(ROOT)}")
    print(f"OK: seeded {len(SEEDS)} citations")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
