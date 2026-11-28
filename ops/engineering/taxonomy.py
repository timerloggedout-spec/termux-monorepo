"""Engineering taxonomy validator and query CLI.

The registry is a sibling domain to Reverse Engineering and uses only the
Python standard library.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent


def load_taxonomy(path: str | Path | None = None) -> dict[str, Any]:
    """Load the canonical engineering taxonomy JSON."""
    source = Path(path) if path else HERE / "taxonomy.json"
    return json.loads(source.read_text(encoding="utf-8"))


def validate(taxonomy: dict[str, Any]) -> list[str]:
    """Return taxonomy, graph, metadata and toolchain validation errors."""
    errors: list[str] = []
    if taxonomy.get("schema") != "engineering-taxonomy/v1":
        errors.append("schema must be engineering-taxonomy/v1")

    nodes = taxonomy.get("nodes") or []
    by_id: dict[str, dict[str, Any]] = {}
    for item in nodes:
        node_id = item.get("id")
        if not isinstance(node_id, str) or not node_id:
            errors.append("every node needs a non-empty id")
            continue
        if node_id in by_id:
            errors.append(f"duplicate node id {node_id!r}")
        by_id[node_id] = item
        if item.get("kind") not in ("category", "tool"):
            errors.append(f"{node_id}: kind must be category|tool")

    axes = taxonomy.get("axes") or {}
    for node_id, item in by_id.items():
        parents = item.get("parents", [])
        if not isinstance(parents, list):
            errors.append(f"{node_id}: parents must be a list")
            continue
        for parent in parents:
            if parent not in by_id:
                errors.append(f"{node_id}: unknown parent {parent!r}")

        tags = item.get("tags") or {}
        for axis, values in tags.items():
            if axis not in axes:
                errors.append(f"{node_id}: unknown axis {axis!r}")
                continue
            if not isinstance(values, list):
                errors.append(f"{node_id}: axis {axis!r} values must be a list")
                continue
            for value in values:
                if value not in axes[axis]:
                    errors.append(f"{node_id}: unknown {axis} value {value!r}")

        if item.get("kind") != "tool":
            continue

        metadata = item.get("metadata") or {}
        required = (
            "license",
            "license_class",
            "access",
            "payment_card_required",
            "commercial_use",
            "execution_target",
            "probe_commands",
            "source_url",
        )
        for field in required:
            if field not in metadata:
                errors.append(f"{node_id}: missing metadata field {field!r}")

        if metadata.get("license_class") not in ("foss", "proprietary"):
            errors.append(f"{node_id}: invalid license_class")
        if metadata.get("access") not in (axes.get("access") or []):
            errors.append(f"{node_id}: invalid access class")
        if metadata.get("payment_card_required") not in (True, False, "unknown"):
            errors.append(f"{node_id}: payment_card_required must be boolean or unknown")
        if not isinstance(metadata.get("probe_commands"), list) or not all(
            isinstance(command, str) for command in metadata.get("probe_commands", [])
        ):
            errors.append(f"{node_id}: probe_commands must be a list of strings")
        if not str(metadata.get("source_url", "")).startswith("https://"):
            errors.append(f"{node_id}: source_url must use HTTPS")
        if not (item.get("tags") or {}).get("tool_role"):
            errors.append(f"{node_id}: tool requires a tool_role tag")

    root = by_id.get("engineering")
    if root is None or root.get("parents") != []:
        errors.append("engineering root node is missing or has parents")

    white, gray, black = 0, 1, 2
    colors = {node_id: white for node_id in by_id}

    def visit(node_id: str, trail: list[str]) -> None:
        colors[node_id] = gray
        for parent in by_id[node_id].get("parents", []):
            if parent not in by_id:
                continue
            if colors[parent] == gray:
                errors.append(f"parent cycle: {' -> '.join(trail + [node_id, parent])}")
            elif colors[parent] == white:
                visit(parent, trail + [node_id])
        colors[node_id] = black

    for node_id in by_id:
        if colors[node_id] == white:
            visit(node_id, [])

    def reaches_root(node_id: str, ancestors: set[str] | None = None) -> bool:
        path = set() if ancestors is None else set(ancestors)
        if node_id == "engineering":
            return True
        if node_id in path:
            return False
        path.add(node_id)
        return any(
            parent in by_id and reaches_root(parent, path)
            for parent in by_id[node_id].get("parents", [])
        )

    for node_id in by_id:
        if node_id != "engineering" and not reaches_root(node_id):
            errors.append(f"{node_id}: does not descend from engineering")

    stages = taxonomy.get("workflow_stages") or []
    for chain in taxonomy.get("toolchains") or []:
        category = chain.get("category")
        if category not in by_id or by_id[category].get("kind") != "category":
            errors.append(
                f"toolchain {chain.get('id')!r}: unknown category {category!r}"
            )

        last_index = -1
        for step in chain.get("stages", []):
            stage = step.get("stage")
            if stage not in stages:
                errors.append(f"toolchain {chain.get('id')!r}: unknown stage {stage!r}")
                continue
            stage_index = stages.index(stage)
            if stage_index < last_index:
                errors.append(f"toolchain {chain.get('id')!r}: stages out of order")
            last_index = stage_index

            for tool_id in step.get("tools", []):
                if tool_id not in by_id or by_id[tool_id].get("kind") != "tool":
                    errors.append(
                        f"toolchain {chain.get('id')!r}: {tool_id!r} is not a tool"
                    )

    matrix = taxonomy.get("overlap_matrix") or {}
    for row_id, row in (matrix.get("rows") or {}).items():
        if row_id not in by_id:
            errors.append(f"overlap row {row_id!r} is not a node")
        for method, value in row.items():
            if method not in (matrix.get("methods") or []):
                errors.append(f"overlap {row_id}: unknown method {method!r}")
            if value not in (matrix.get("values") or []):
                errors.append(f"overlap {row_id}: invalid value {value!r}")

    return errors


def node(taxonomy: dict[str, Any], node_id: str) -> dict[str, Any] | None:
    """Return a node and its immediate children."""
    for item in taxonomy.get("nodes", []):
        if item.get("id") == node_id:
            children = [
                candidate["id"]
                for candidate in taxonomy["nodes"]
                if node_id in candidate.get("parents", [])
            ]
            return {**item, "children": children}
    return None


def toolchain(taxonomy: dict[str, Any], chain_id: str) -> dict[str, Any] | None:
    """Return one ordered toolchain by stable ID."""
    return next(
        (item for item in taxonomy.get("toolchains", []) if item.get("id") == chain_id),
        None,
    )


def main(argv: list[str] | None = None) -> int:
    args = list(sys.argv[1:] if argv is None else argv)
    taxonomy = load_taxonomy()
    command = args[0] if args else "validate"

    if command == "validate":
        errors = validate(taxonomy)
        if errors:
            print("\n".join(errors))
            return 1
        print(
            "engineering-taxonomy/v1: valid "
            f"({len(taxonomy['nodes'])} nodes, {len(taxonomy['toolchains'])} toolchains)"
        )
        return 0

    if command == "node" and len(args) == 2:
        result = node(taxonomy, args[1])
        if result is None:
            print(f"unknown engineering node: {args[1]}", file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    if command == "toolchain" and len(args) == 2:
        result = toolchain(taxonomy, args[1])
        if result is None:
            print(f"unknown engineering toolchain: {args[1]}", file=sys.stderr)
            return 1
        print(json.dumps(result, indent=2, sort_keys=True))
        return 0

    print(__doc__)
    return 2


if __name__ == "__main__":
    sys.exit(main())
