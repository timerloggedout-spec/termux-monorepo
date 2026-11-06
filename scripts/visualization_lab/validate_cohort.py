#!/usr/bin/env python3
"""Validate the deterministic synthetic visualization renderer cohort."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
FIXTURE = ROOT / "experiments/visualization-renderers/fixtures/renderer-cohort-v1.json"


def validate(payload: dict) -> list[str]:
    errors: list[str] = []
    if payload.get("schema") != "renderer-cohort/v1":
        errors.append("schema must be renderer-cohort/v1")
    if payload.get("data_class") != "synthetic":
        errors.append("data_class must remain synthetic")
    if not payload.get("fixture_id"):
        errors.append("fixture_id is required")

    hierarchy = payload.get("hierarchy")
    if not isinstance(hierarchy, dict) or not hierarchy.get("id"):
        errors.append("hierarchy root with stable id is required")

    network = payload.get("network") or {}
    nodes = network.get("nodes") or []
    edges = network.get("edges") or []
    node_ids = [n.get("id") for n in nodes if isinstance(n, dict)]
    if len(node_ids) != len(nodes) or not node_ids or len(set(node_ids)) != len(node_ids):
        errors.append("network node ids must be present and unique")
    known = set(node_ids)
    edge_ids = [e.get("id") for e in edges if isinstance(e, dict)]
    if len(edge_ids) != len(edges) or len(set(edge_ids)) != len(edge_ids):
        errors.append("network edge ids must be present and unique")
    for edge in edges:
        if edge.get("source") not in known or edge.get("target") not in known:
            errors.append(f"edge {edge.get('id')} references an unknown endpoint")

    series = payload.get("series") or {}
    points = series.get("points") or []
    if len(points) < 2:
        errors.append("series needs at least two observations")
    previous = ""
    for point in points:
        if not isinstance(point, dict) or not point.get("t"):
            errors.append("every series point needs a timestamp")
            continue
        if point["t"] <= previous:
            errors.append("series timestamps must be strictly increasing")
        previous = point["t"]
        value = point.get("value")
        if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))):
            errors.append("series values must be numeric or null (never coerced)")
    if not series.get("unit"):
        errors.append("series unit is required")
    if not series.get("generated_at"):
        errors.append("series generated_at is required")
    return errors


def main() -> int:
    payload = json.loads(FIXTURE.read_text(encoding="utf-8"))
    errors = validate(payload)
    if errors:
        print("\n".join(f"FAIL: {item}" for item in errors))
        return 1
    print(f"PASS: {payload['fixture_id']} ({len(payload['network']['nodes'])} nodes, "
          f"{len(payload['network']['edges'])} edges, "
          f"{len(payload['series']['points'])} time points)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
