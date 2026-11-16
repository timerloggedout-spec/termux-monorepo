#!/usr/bin/env python3
"""Reproducible, dependency-light DAG planner microbenchmark.

This measures the local Python reference implementation only. If NetworkX is
installed, it also times NetworkX's lexicographical topological sort. It does
not claim to benchmark FalkorDB; that requires a reachable, version-pinned
database and separately recorded network/query costs.
"""
from __future__ import annotations

import argparse
import json
import random
import statistics
import time

from she.orchestration.dag import plan_dag


def make_dag(node_count: int, edge_probability: float, seed: int):
    rng = random.Random(seed)
    nodes = [f"n{i:06d}" for i in range(node_count)]
    edges = []
    for index, source in enumerate(nodes):
        for target in nodes[index + 1 :]:
            if rng.random() < edge_probability:
                edges.append((source, target))
    return nodes, edges


def median_seconds(call, repeats: int) -> tuple[float, object]:
    samples = []
    result = None
    for _ in range(repeats):
        started = time.perf_counter()
        result = call()
        samples.append(time.perf_counter() - started)
    return statistics.median(samples), result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--nodes", type=int, default=500)
    parser.add_argument("--edge-probability", type=float, default=0.004)
    parser.add_argument("--seed", type=int, default=1443)
    parser.add_argument("--repeats", type=int, default=5)
    args = parser.parse_args()
    if args.nodes < 0 or args.repeats < 1:
        parser.error("--nodes must be non-negative and --repeats must be positive")
    if not 0.0 <= args.edge_probability <= 1.0:
        parser.error("--edge-probability must be between 0 and 1")

    nodes, edges = make_dag(args.nodes, args.edge_probability, args.seed)
    seconds, plan = median_seconds(lambda: plan_dag(nodes, edges), args.repeats)
    output = {
        "benchmark": "dag-reference-planner",
        "algorithm_version": plan.algorithm_version,
        "seed": args.seed,
        "node_count": plan.node_count,
        "edge_count": plan.edge_count,
        "repeats": args.repeats,
        "median_seconds": seconds,
        "graph_sha256": plan.graph_sha256,
        "is_acyclic": plan.is_acyclic,
        "networkx_median_seconds": None,
        "networkx_available": False,
        "falkordb_measurement": "not_run",
    }

    try:
        import networkx as nx
    except ImportError:
        nx = None
    if nx is not None:
        graph = nx.DiGraph()
        graph.add_nodes_from(nodes)
        graph.add_edges_from(edges)
        oracle_seconds, oracle_order = median_seconds(
            lambda: tuple(nx.lexicographical_topological_sort(graph, key=str)),
            args.repeats,
        )
        output["networkx_available"] = True
        output["networkx_median_seconds"] = oracle_seconds
        output["networkx_order_matches"] = tuple(plan.topological_order) == tuple(oracle_order)

    print(json.dumps(output, sort_keys=True, indent=2))
    return 0 if output["is_acyclic"] and output.get("networkx_order_matches", True) else 1


if __name__ == "__main__":
    raise SystemExit(main())
