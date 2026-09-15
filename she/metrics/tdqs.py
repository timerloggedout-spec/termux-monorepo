#!/usr/bin/env python3
"""Deterministic TDQS preparation and aggregation primitives.

This module implements the non-LLM half of Glama's Tool Definition Quality
Score (TDQS): context-signal extraction, hard gates, weighted aggregation,
tiering, and server-level rollups. It deliberately does not call a model,
network service, or provider. The six rubric dimension values must come from a
separately recorded evaluator when a full TDQS score is produced.

Source contract: glama-ai/tool-definition-quality-score (TDQS v1.x), with
provenance recorded in ``docs/architecture/TOOL-DEFINITION-QUALITY-SCORE.md``.
"""
from __future__ import annotations

import hashlib
import json
import math
from dataclasses import asdict, dataclass
from typing import Any, Mapping


DIMENSION_WEIGHTS: dict[str, int] = {
    "purpose_clarity": 25,
    "usage_guidelines": 20,
    "behavioral_transparency": 20,
    "parameter_semantics": 15,
    "conciseness_structure": 10,
    "contextual_completeness": 10,
}


def _canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def _definition_fields(tool: Mapping[str, Any]) -> dict[str, Any]:
    return {
        key: tool.get(key)
        for key in ("name", "title", "description", "inputSchema", "outputSchema", "annotations")
    }


def _local_ref(schema: Mapping[str, Any], ref: str) -> Mapping[str, Any] | None:
    if not ref.startswith("#/"):
        return None
    node: Any = schema
    for part in ref[2:].split("/"):
        part = part.replace("~1", "/").replace("~0", "~")
        if not isinstance(node, Mapping) or part not in node:
            return None
        node = node[part]
    return node if isinstance(node, Mapping) else None


def _walk_required(
    schema: Mapping[str, Any] | None,
    root: Mapping[str, Any],
    *,
    depth: int = 0,
    visited: frozenset[str] = frozenset(),
) -> tuple[int, int, int, bool]:
    """Return required-field count, depth, union choices, nested-object flag."""
    if not schema:
        return 0, 0, 0, False

    if "$ref" in schema:
        ref = schema.get("$ref")
        if isinstance(ref, str) and ref not in visited:
            target = _local_ref(root, ref)
            if target is not None:
                return _walk_required(target, root, depth=depth, visited=visited | {ref})
        return 0, depth, 0, False

    branch_counts: list[tuple[int, int, int, bool]] = []
    for key in ("oneOf", "anyOf"):
        branches = schema.get(key)
        if isinstance(branches, list):
            for branch in branches:
                if isinstance(branch, Mapping):
                    branch_counts.append(_walk_required(branch, root, depth=depth, visited=visited))
            break

    own_type = schema.get("type")
    is_object = own_type == "object" or isinstance(schema.get("properties"), Mapping)
    nested_object = is_object and depth > 0

    if branch_counts:
        chosen = max(branch_counts, key=lambda item: item[0])
        required_count, max_depth, unions, nested = chosen
        # Nullable unions are not invocation choices in TDQS.
        non_null_branches = [
            branch
            for branch in (schema.get("oneOf") or schema.get("anyOf") or [])
            if not (isinstance(branch, Mapping) and branch.get("type") == "null")
        ]
        union_choices = max(0, len(non_null_branches) - 1)
        return required_count, max_depth, unions + union_choices, nested or nested_object

    if is_object:
        properties = schema.get("properties")
        required = schema.get("required")
        required_names = required if isinstance(required, list) else []
        count = 1 if depth > 0 else 0
        max_depth = max(1, depth) if properties is not None else depth
        unions = 0
        nested = nested_object
        if isinstance(properties, Mapping):
            for name in required_names:
                child = properties.get(name)
                if not isinstance(child, Mapping):
                    continue
                child_count, child_depth, child_unions, child_nested = _walk_required(
                    child, root, depth=depth + 1, visited=visited
                )
                count += child_count
                max_depth = max(max_depth, child_depth)
                unions += child_unions
                nested = nested or child_nested or child.get("type") == "object"
        return count, max_depth, unions, nested

    if own_type == "array":
        items = schema.get("items")
        if isinstance(items, Mapping):
            return _walk_required(items, root, depth=depth + 1, visited=visited)

    return 1 if depth > 0 else 0, depth, 0, nested_object


def _iter_required_properties(schema: Mapping[str, Any] | None) -> list[tuple[str, Mapping[str, Any]]]:
    if not isinstance(schema, Mapping):
        return []
    properties = schema.get("properties")
    required = schema.get("required")
    if not isinstance(properties, Mapping) or not isinstance(required, list):
        return []
    return [(name, properties[name]) for name in required if isinstance(name, str) and isinstance(properties.get(name), Mapping)]


@dataclass(frozen=True)
class TDQSContextSignals:
    param_count: int
    required_param_count: int
    params_with_descriptions: int
    params_with_enums: int
    schema_description_coverage: int
    has_nested_objects: bool
    required_field_count: int
    schema_depth: int
    union_choice_count: int
    invocation_cost: int
    has_output_schema: bool
    has_annotations: bool
    annotation_values: dict[str, bool | None]
    title_is_meaningful: bool
    definition_bytes: int
    input_hash: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def context_signals(tool: Mapping[str, Any]) -> TDQSContextSignals:
    """Extract deterministic TDQS context signals from one MCP tool definition."""
    schema = tool.get("inputSchema")
    schema = schema if isinstance(schema, Mapping) else None
    properties = schema.get("properties") if schema else None
    properties = properties if isinstance(properties, Mapping) else {}
    required = schema.get("required") if schema else []
    required = required if isinstance(required, list) else []

    param_count = len(properties)
    params_with_descriptions = sum(
        1 for value in properties.values() if isinstance(value, Mapping) and str(value.get("description", "")).strip()
    )
    params_with_enums = sum(
        1 for value in properties.values() if isinstance(value, Mapping) and isinstance(value.get("enum"), list)
    )
    coverage = round(params_with_descriptions / param_count * 100) if param_count else 100

    required_fields, depth, unions, nested = _walk_required(schema, schema or {})
    invocation_cost = required_fields + 2 * max(0, depth - 1) + 2 * unions

    output_schema = tool.get("outputSchema")
    annotations = tool.get("annotations")
    annotations = annotations if isinstance(annotations, Mapping) else None
    name = str(tool.get("name") or "")
    title = tool.get("title")
    title_is_meaningful = bool(title and str(title) != name and len(str(title)) > len(name))

    fields = _definition_fields(tool)
    serialized = _canonical(fields).encode("utf-8")
    input_hash = hashlib.sha256(serialized).hexdigest()[:16]

    annotation_values = {
        key: (bool(annotations[key]) if annotations and key in annotations else None)
        for key in ("readOnlyHint", "destructiveHint", "idempotentHint", "openWorldHint")
    }

    return TDQSContextSignals(
        param_count=param_count,
        required_param_count=len(required),
        params_with_descriptions=params_with_descriptions,
        params_with_enums=params_with_enums,
        schema_description_coverage=coverage,
        has_nested_objects=nested,
        required_field_count=required_fields,
        schema_depth=depth,
        union_choice_count=unions,
        invocation_cost=invocation_cost,
        has_output_schema=isinstance(output_schema, Mapping) and bool(output_schema),
        has_annotations=bool(annotations),
        annotation_values=annotation_values,
        title_is_meaningful=title_is_meaningful,
        definition_bytes=len(serialized),
        input_hash=input_hash,
    )


def tier(score: float) -> str:
    if score >= 3.5:
        return "A"
    if score >= 3.0:
        return "B"
    if score >= 2.0:
        return "C"
    if score >= 1.0:
        return "D"
    return "F"


def weighted_score(dimensions: Mapping[str, float]) -> float:
    """Aggregate the six 1–5 rubric dimensions into TDQS, rounded to 1 decimal."""
    missing = set(DIMENSION_WEIGHTS) - set(dimensions)
    extra = set(dimensions) - set(DIMENSION_WEIGHTS)
    if missing or extra:
        raise ValueError(f"dimension keys mismatch; missing={sorted(missing)} extra={sorted(extra)}")
    for name, value in dimensions.items():
        if not math.isfinite(float(value)) or not 1.0 <= float(value) <= 5.0:
            raise ValueError(f"{name} must be within 1–5")
    return round(sum(float(dimensions[name]) * weight for name, weight in DIMENSION_WEIGHTS.items()) / 100, 1)


def hard_gates(tool: Mapping[str, Any]) -> dict[str, Any]:
    """Return deterministic gate/flag information before LLM rubric evaluation."""
    description = str(tool.get("description") or "").strip()
    name = str(tool.get("name") or "").strip().lower()
    title = str(tool.get("title") or "").strip().lower()
    missing_description = not description
    tautological = bool(description and description.lower() in {name, title} - {""})
    return {
        "missing_description": missing_description,
        "tautological_description": tautological,
        "flags": (["No Description"] if missing_description else []) + (["Tautological Description"] if tautological else []),
    }


def apply_post_processing(tool: Mapping[str, Any], dimensions: Mapping[str, float]) -> dict[str, Any]:
    """Apply TDQS hard-gate/tautology behavior to supplied LLM dimension scores."""
    gates = hard_gates(tool)
    if gates["missing_description"]:
        final_dimensions = {name: 1.0 for name in DIMENSION_WEIGHTS}
    else:
        final_dimensions = {name: float(value) for name, value in dimensions.items()}
        if gates["tautological_description"]:
            final_dimensions["purpose_clarity"] = min(final_dimensions["purpose_clarity"], 2.0)
    score = weighted_score(final_dimensions)
    return {"dimensions": final_dimensions, "score": score, "tier": tier(score), **gates}


def server_definition_quality(tool_scores: list[float]) -> float:
    """Glama's server-level definition-quality rollup: 60% mean + 40% minimum."""
    if not tool_scores:
        raise ValueError("at least one tool score is required")
    if any(not 1.0 <= float(score) <= 5.0 for score in tool_scores):
        raise ValueError("tool scores must be within 1–5")
    return round(0.6 * (sum(tool_scores) / len(tool_scores)) + 0.4 * min(tool_scores), 1)


def overall_server_score(definition_quality: float, coherence: float) -> float:
    """Combine TDQS definition quality (70%) with server coherence (30%)."""
    if not (1.0 <= float(definition_quality) <= 5.0 and 1.0 <= float(coherence) <= 5.0):
        raise ValueError("server component scores must be within 1–5")
    return round(0.7 * float(definition_quality) + 0.3 * float(coherence), 1)
