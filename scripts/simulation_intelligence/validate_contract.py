#!/usr/bin/env python3
"""Offline structural and safety checks for SIP v1 contracts.

This is intentionally a small contract guard, not a full JSON Schema engine.
The adjacent JSON Schemas remain the normative structural contracts.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

HEX64 = re.compile(r"^[0-9a-f]{64}$")
HEX40 = re.compile(r"^[0-9a-f]{40}$")
RUN_STATES = {
    "prepared", "admitted", "queued", "starting", "running", "paused",
    "stopping", "finalizing", "completed", "failed", "cancelled",
    "blocked", "recovery_required",
}
KINDS = {"scenario", "run-manifest", "event", "graph-delta"}


def _is_object(value: Any) -> bool:
    return isinstance(value, dict)


def validate(kind: str, value: Any) -> list[str]:
    errors: list[str] = []
    if kind not in KINDS:
        return [f"unsupported contract kind: {kind}"]
    if not _is_object(value):
        return ["root must be an object"]

    if kind == "scenario":
        if value.get("schema_version") != "sip.scenario.v1":
            errors.append("schema_version must be sip.scenario.v1")
        for field in ("scenario_id", "title", "objective"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                errors.append(f"{field} must be a non-empty string")
        cohort = value.get("source_cohort")
        if not _is_object(cohort):
            errors.append("source_cohort must be an object")
        elif not HEX64.fullmatch(str(cohort.get("evidence_manifest_sha256", ""))):
            errors.append("source_cohort.evidence_manifest_sha256 must be sha256")
        graph = value.get("graph_snapshot")
        if not _is_object(graph):
            errors.append("graph_snapshot must be an object")
        else:
            if not HEX64.fullmatch(str(graph.get("sha256", ""))):
                errors.append("graph_snapshot.sha256 must be sha256")
            if graph.get("layer") not in {"source_graph", "derived_graph"}:
                errors.append("graph_snapshot.layer must be source_graph or derived_graph")
        env = value.get("environment")
        if not _is_object(env):
            errors.append("environment must be an object")
        else:
            if not isinstance(env.get("max_agents"), int) or env["max_agents"] < 1:
                errors.append("environment.max_agents must be a positive integer")
            if not isinstance(env.get("max_steps"), int) or env["max_steps"] < 1:
                errors.append("environment.max_steps must be a positive integer")
            probability = env.get("activation_probability")
            if not isinstance(probability, (int, float)) or not 0 <= probability <= 1:
                errors.append("environment.activation_probability must be between 0 and 1")
            if env.get("public_platform_actions") is not False:
                errors.append("public_platform_actions must be false")
    elif kind == "run-manifest":
        if value.get("schema_version") != "sip.run-manifest.v1":
            errors.append("schema_version must be sip.run-manifest.v1")
        for field in ("run_id", "scenario_id", "experiment_id"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                errors.append(f"{field} must be a non-empty string")
        if value.get("status") not in RUN_STATES:
            errors.append("status is not a recognized SIP lifecycle state")
        repro = value.get("reproducibility")
        if not _is_object(repro):
            errors.append("reproducibility must be an object")
        else:
            if not HEX40.fullmatch(str(repro.get("repository_sha", ""))):
                errors.append("reproducibility.repository_sha must be a 40-character SHA")
            for field in ("scenario_sha256", "graph_sha256", "config_sha256"):
                if not HEX64.fullmatch(str(repro.get(field, ""))):
                    errors.append(f"reproducibility.{field} must be sha256")
            if not isinstance(repro.get("seed"), int) or repro["seed"] < 0:
                errors.append("reproducibility.seed must be a non-negative integer")
        limits = value.get("limits")
        if not _is_object(limits):
            errors.append("limits must be an object")
        else:
            for field in ("agents", "steps", "wall_seconds", "max_concurrent_runs"):
                if not isinstance(limits.get(field), int) or limits[field] < 1:
                    errors.append(f"limits.{field} must be a positive integer")
    elif kind == "event":
        if value.get("schema_version") != "sip.event.v1":
            errors.append("schema_version must be sip.event.v1")
        for field in ("event_id", "run_id", "event_type", "idempotency_key"):
            if not isinstance(value.get(field), str) or not value[field].strip():
                errors.append(f"{field} must be a non-empty string")
        if not isinstance(value.get("sequence"), int) or value["sequence"] < 0:
            errors.append("sequence must be a non-negative integer")
        if not HEX64.fullmatch(str(value.get("payload_digest", ""))):
            errors.append("payload_digest must be sha256")
        provenance = value.get("provenance")
        if not _is_object(provenance) or provenance.get("source") not in {
            "oasis", "mirofish-adapter", "mesa", "deterministic-fake", "supervisor"
        }:
            errors.append("provenance.source must identify a supported event producer")
        privacy = value.get("privacy")
        if not _is_object(privacy) or privacy.get("contains_secret") is not False or privacy.get("contains_raw_prompt") is not False:
            errors.append("event must explicitly exclude secrets and raw prompts")
        agent_id = value.get("agent_id")
        if agent_id is not None and (not isinstance(agent_id, str) or not agent_id.startswith("synthetic:")):
            errors.append("agent_id must be null or explicitly synthetic")
    elif kind == "graph-delta":
        if value.get("schema_version") != "sip.graph-delta.v1":
            errors.append("schema_version must be sip.graph-delta.v1")
        if not HEX64.fullmatch(str(value.get("base_graph_sha256", ""))):
            errors.append("base_graph_sha256 must be sha256")
        if value.get("promotion_state") != "not_promotable_from_simulation_alone":
            errors.append("simulation graph delta cannot be promoted from simulation alone")
        for node in value.get("nodes", []):
            if not _is_object(node) or node.get("synthetic") is not True or not str(node.get("id", "")).startswith("synthetic:"):
                errors.append("every graph-delta node must be explicitly synthetic")
        for edge in value.get("edges", []):
            if not _is_object(edge) or edge.get("evidence_class") != "simulation_observation":
                errors.append("every graph-delta edge must be simulation_observation")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("kind", choices=sorted(KINDS))
    parser.add_argument("path", type=Path)
    args = parser.parse_args(argv)
    try:
        payload = json.loads(args.path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 2
    errors = validate(args.kind, payload)
    if errors:
        for error in errors:
            print(f"ERROR: {error}", file=sys.stderr)
        return 1
    print(f"VALID: {args.kind}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
