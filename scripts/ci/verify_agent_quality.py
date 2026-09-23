#!/usr/bin/env python3
"""Verify the minimum documentation and safety contract for agent telemetry code.

This is deliberately a static quality gate: it does not execute agent payloads,
inspect secrets, or score throughput. Its job is to catch undocumented/non-obvious
measurement logic before the broader review/evidence lanes consume it.
"""
from __future__ import annotations

import ast
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "she/metrics/agent_throughput.py"
SCHEMA = ROOT / "docs/ops/AGENT-THROUGHPUT-EVENT.schema.json"
METRICS_DOC = ROOT / "docs/ops/AGENT-THROUGHPUT-METRICS.md"
PRIORITY_DOC = ROOT / "docs/ops/AGENT-OBSERVABILITY-PRIORITY-DECISION.md"
TDQS_SOURCE = ROOT / "she/metrics/tdqs.py"
TDQS_SCHEMA = ROOT / "docs/ops/TDQS-EVIDENCE.schema.json"
TDQS_DOC = ROOT / "docs/architecture/TOOL-DEFINITION-QUALITY-SCORE.md"
IMPROVEMENT_POLICY = ROOT / "docs/ops/CONTINUOUS-IMPROVEMENT-POLICY.md"


def require(condition: bool, message: str) -> None:
    """Fail with an actionable message instead of silently weakening the gate."""
    if not condition:
        raise SystemExit(f"QUALITY-LANE FAILURE: {message}")


def main() -> None:
    """Run deterministic source, documentation, and policy checks."""
    require(SOURCE.is_file(), f"missing implementation: {SOURCE}")
    require(SCHEMA.is_file(), f"missing event schema: {SCHEMA}")
    require(METRICS_DOC.is_file(), f"missing metrics contract: {METRICS_DOC}")
    require(PRIORITY_DOC.is_file(), f"missing observability priority record: {PRIORITY_DOC}")
    require(TDQS_SOURCE.is_file(), f"missing TDQS reducer: {TDQS_SOURCE}")
    require(TDQS_SCHEMA.is_file(), f"missing TDQS evidence schema: {TDQS_SCHEMA}")
    require(TDQS_DOC.is_file(), f"missing TDQS integration document: {TDQS_DOC}")
    require(IMPROVEMENT_POLICY.is_file(), f"missing continuous improvement policy: {IMPROVEMENT_POLICY}")

    source = SOURCE.read_text(encoding="utf-8")
    tree = ast.parse(source, filename=str(SOURCE))

    # Public measurement surfaces need docstrings so later maintainers can audit
    # the mathematical intent without reverse-engineering the reducer.
    require(ast.get_docstring(tree) is not None, "agent_throughput.py needs a module docstring")
    public_nodes = [
        node
        for node in tree.body
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef))
        and not node.name.startswith("_")
    ]
    missing = [node.name for node in public_nodes if ast.get_docstring(node) is None]
    require(not missing, f"public symbols need docstrings: {', '.join(missing)}")

    # Keep the non-obvious metric formulas visibly documented in the source.
    required_comments = (
        "# Sequential baseline is only valid when",
        "# Keep throughput observational",
    )
    for marker in required_comments:
        require(marker in source, f"missing explanatory source comment: {marker}")

    # The repository policy explicitly forbids converting ATES into a merge gate.
    require("MIN_ATES_THRESHOLD" not in source, "speed-only MIN_ATES_THRESHOLD must not be introduced")

    metrics_doc = METRICS_DOC.read_text(encoding="utf-8")
    priority_doc = PRIORITY_DOC.read_text(encoding="utf-8")
    tdqs_source = TDQS_SOURCE.read_text(encoding="utf-8")
    tdqs_doc = TDQS_DOC.read_text(encoding="utf-8")
    improvement_policy = IMPROVEMENT_POLICY.read_text(encoding="utf-8")
    require("quality > time" in metrics_doc, "metrics contract must preserve quality-first policy")
    require("Phase A" in metrics_doc and "Phase B" in metrics_doc, "metrics phases A/B must be documented")
    require("COMMITTED" in metrics_doc and "VALIDATED" in metrics_doc, "evidence states must remain explicit")
    require("Codespaces" in priority_doc and "Docker" in priority_doc, "environment lanes must remain documented")
    require("TDQS_SPEC_VERSION = \"1.3\"" in tdqs_source, "TDQS spec provenance must remain explicit")
    require("ATES" in tdqs_doc and "AEF" in tdqs_doc, "TDQS semantic boundary must remain explicit")
    require("Observe" in improvement_policy and "Recompare" in improvement_policy, "continuous learning loop must remain explicit")
    require("Context Relationship Graph" in improvement_policy and "Jules" in improvement_policy, "curated external lessons must remain incorporated")

    print("QUALITY-LANE PASS: telemetry code is documented, policy-safe, and contract-linked")


if __name__ == "__main__":
    main()
