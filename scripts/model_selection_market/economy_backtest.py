"""Deterministic paper-economy simulation and scenario backtesting.

Synthetic cohorts are exploratory. The engine never connects to wallets,
signers, networks, or production accounting.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import random
from pathlib import Path
from typing import Any

SIMULATION_VERSION = "economy-backtest/v1"
BPS = 10_000
MAX_UNITS = 2**63 - 1


def canonical(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=False, allow_nan=False)


def digest(value: Any) -> str:
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def _integer(value: Any, name: str, low: int, high: int) -> int:
    if type(value) is not int or not low <= value <= high:
        raise ValueError(f"{name} must be an integer in [{low}, {high}]")
    return value


def validate_manifest(manifest: dict[str, Any]) -> dict[str, Any]:
    required = {
        "schema_version", "scenario_id", "seed", "horizon_rounds",
        "reward_units", "participants", "policy",
    }
    if not isinstance(manifest, dict) or set(manifest) != required:
        raise ValueError("manifest fields must match economy-backtest/v1")
    if type(manifest["schema_version"]) is not int or manifest["schema_version"] != 1:
        raise ValueError("unsupported manifest schema_version")
    if not isinstance(manifest["scenario_id"], str) or not manifest["scenario_id"].strip():
        raise ValueError("scenario_id must be non-empty")
    seed = _integer(manifest["seed"], "seed", 0, 2**63 - 1)
    rounds = _integer(manifest["horizon_rounds"], "horizon_rounds", 1, 10_000)
    reward = _integer(manifest["reward_units"], "reward_units", 1, MAX_UNITS)
    participants = manifest["participants"]
    if not isinstance(participants, list) or not participants:
        raise ValueError("participants must be a non-empty array")
    ids = set()
    normalized = []
    for row in participants:
        if not isinstance(row, dict) or set(row) != {
            "participant_id", "success_probability_bps", "initial_balance", "origin_id"
        }:
            raise ValueError("participant fields must match the cohort schema")
        actor = row["participant_id"]
        if not isinstance(actor, str) or not actor.strip() or actor in ids:
            raise ValueError("participant_id values must be unique and non-empty")
        ids.add(actor)
        normalized.append({
            "participant_id": actor,
            "success_probability_bps": _integer(
                row["success_probability_bps"], "success_probability_bps", 0, BPS),
            "initial_balance": _integer(row["initial_balance"], "initial_balance", 0, MAX_UNITS),
            "origin_id": row["origin_id"],
        })
    for row in normalized:
        origin = row["origin_id"]
        if origin is not None and (not isinstance(origin, str) or origin not in ids):
            raise ValueError("origin_id must reference a cohort participant or null")
    policy = manifest["policy"]
    if not isinstance(policy, dict) or set(policy) != {
        "policy_id", "cull_after_misses", "pool_distribution_bps", "royalty_rate_bps"
    }:
        raise ValueError("policy fields must match economy-backtest/v1")
    if not isinstance(policy["policy_id"], str) or not policy["policy_id"].strip():
        raise ValueError("policy_id must be non-empty")
    policy = {
        "policy_id": policy["policy_id"],
        "cull_after_misses": _integer(policy["cull_after_misses"], "cull_after_misses", 1, rounds + 1),
        "pool_distribution_bps": _integer(
            policy["pool_distribution_bps"], "pool_distribution_bps", 0, BPS),
        "royalty_rate_bps": _integer(policy["royalty_rate_bps"], "royalty_rate_bps", 0, BPS),
    }
    return {
        "schema_version": 1, "scenario_id": manifest["scenario_id"],
        "seed": seed, "horizon_rounds": rounds, "reward_units": reward,
        "participants": sorted(normalized, key=lambda row: row["participant_id"]),
        "policy": policy,
    }


def _gini(values: list[int]) -> float:
    ordered = sorted(values)
    total = sum(ordered)
    if not ordered or total == 0:
        return 0.0
    n = len(ordered)
    weighted = sum((i + 1) * value for i, value in enumerate(ordered))
    return (2 * weighted) / (n * total) - (n + 1) / n


def _allocate(pool: int, recipients: list[str], weights: dict[str, int]) -> dict[str, int]:
    eligible = [actor for actor in sorted(recipients) if weights.get(actor, 0) > 0]
    total_weight = sum(weights[actor] for actor in eligible)
    if pool <= 0 or total_weight <= 0:
        return {}
    allocations = {
        actor: (pool * weights[actor]) // total_weight for actor in eligible
    }
    remainder = pool - sum(allocations.values())
    for actor in eligible:
        if remainder == 0:
            break
        allocations[actor] += 1
        remainder -= 1
    return {actor: units for actor, units in allocations.items() if units}


def run_backtest(raw_manifest: dict[str, Any]) -> dict[str, Any]:
    manifest = validate_manifest(raw_manifest)
    rng = random.Random(manifest["seed"])
    policy = manifest["policy"]
    actors = {
        row["participant_id"]: {
            "balance": row["initial_balance"], "origin_id": row["origin_id"],
            "success_probability_bps": row["success_probability_bps"],
            "miss_streak": 0, "successes": 0, "attempts": 0,
            "status": "active",
        }
        for row in manifest["participants"]
    }
    initial_units = sum(row["initial_balance"] for row in manifest["participants"])
    issued = 0
    pool = 0
    pool_inflow = 0
    pool_distributed = 0
    royalty_payable: dict[str, int] = {}
    royalty_accrued = 0
    successful_tasks = 0
    attempts = 0
    events: list[dict[str, Any]] = []

    def emit(kind: str, payload: dict[str, Any]) -> None:
        events.append({"seq": len(events) + 1, "type": kind, "payload": payload})

    for actor in sorted(actors):
        emit("genesis", {"participant": actor, "units": actors[actor]["balance"]})

    for round_number in range(1, manifest["horizon_rounds"] + 1):
        for actor in sorted(actors):
            state = actors[actor]
            if state["status"] != "active":
                continue
            state["attempts"] += 1
            attempts += 1
            success = rng.randrange(BPS) < state["success_probability_bps"]
            if success:
                state["miss_streak"] = 0
                state["successes"] += 1
                successful_tasks += 1
                gross = manifest["reward_units"]
                origin = state["origin_id"]
                royalty = 0
                if origin is not None and origin != actor:
                    royalty = (gross * policy["royalty_rate_bps"]) // BPS
                    if royalty:
                        royalty_payable[origin] = royalty_payable.get(origin, 0) + royalty
                        royalty_accrued += royalty
                        emit("royalty_accrual", {
                            "round": round_number, "derivative_actor": actor,
                            "origin_beneficiary": origin, "basis_units": gross,
                            "rate_bps": policy["royalty_rate_bps"], "payable_units": royalty,
                        })
                net = gross - royalty
                state["balance"] += net
                issued += gross
                emit("task_reward", {
                    "round": round_number, "participant": actor,
                    "gross_units": gross, "royalty_units": royalty, "net_units": net,
                })
            else:
                state["miss_streak"] += 1
                emit("task_miss", {"round": round_number, "participant": actor,
                                   "miss_streak": state["miss_streak"]})
                if state["miss_streak"] >= policy["cull_after_misses"]:
                    moved = state["balance"]
                    state["balance"] = 0
                    state["status"] = "culled"
                    pool += moved
                    pool_inflow += moved
                    emit("cull", {
                        "round": round_number, "culled_participant": actor,
                        "wallet_balance_at_cull": moved,
                        "pool_destination": "promotions-incentives-bonuses",
                    })

        active = [actor for actor, state in actors.items() if state["status"] == "active"]
        distributable = (pool * policy["pool_distribution_bps"]) // BPS
        allocations = _allocate(
            distributable, active,
            {actor: actors[actor]["successes"] for actor in active},
        )
        distributed = sum(allocations.values())
        if distributed:
            for actor, units in allocations.items():
                actors[actor]["balance"] += units
            pool -= distributed
            pool_distributed += distributed
            emit("pool_distribution", {
                "round": round_number, "allocations": allocations,
                "distributed_units": distributed, "pool_remainder": pool,
            })

    balances = {actor: state["balance"] for actor, state in sorted(actors.items())}
    payable_total = sum(royalty_payable.values())
    balance_total = sum(balances.values())
    conservation = initial_units + issued - balance_total - pool - payable_total
    if conservation != 0:
        raise AssertionError(f"economy conservation residual: {conservation}")
    total_attempts = attempts
    shares = [value / balance_total for value in balances.values() if value > 0] if balance_total else []
    metrics = {
        "initial_units": initial_units,
        "issued_units": issued,
        "participant_balance_units": balance_total,
        "pool_inflow_units": pool_inflow,
        "pool_distributed_units": pool_distributed,
        "pool_remainder_units": pool,
        "royalty_accrued_units": royalty_accrued,
        "royalty_payable_units": payable_total,
        "royalty_beneficiaries": len(royalty_payable),
        "attempts": total_attempts,
        "successful_tasks": successful_tasks,
        "task_success_rate": successful_tasks / total_attempts if total_attempts else 0.0,
        "active_participants": sum(state["status"] == "active" for state in actors.values()),
        "culled_participants": sum(state["status"] == "culled" for state in actors.values()),
        "retention_rate": sum(state["status"] == "active" for state in actors.values()) / len(actors),
        "pool_recycling_rate": pool_distributed / pool_inflow if pool_inflow else 0.0,
        "balance_gini": _gini(list(balances.values())),
        "balance_hhi": sum(share * share for share in shares),
        "conservation_residual_units": conservation,
    }
    source_digest = digest({
        "scenario_id": manifest["scenario_id"],
        "participants": manifest["participants"],
        "seed": manifest["seed"],
    })
    run_manifest = {
        "simulation_version": SIMULATION_VERSION,
        "manifest": manifest,
        "source": {"kind": "synthetic_cohort", "version": "cohort/v1",
                   "digest": source_digest},
        "manifest_digest": digest(manifest),
    }
    run_id = digest(run_manifest)
    result = {
        "run_id": run_id,
        "simulation_version": SIMULATION_VERSION,
        "manifest_digest": run_manifest["manifest_digest"],
        "source": run_manifest["source"],
        "policy_id": policy["policy_id"],
        "seed": manifest["seed"],
        "metrics": metrics,
        "balances": balances,
        "royalty_payable_by_origin": dict(sorted(royalty_payable.items())),
        "events": events,
        "verdict": "exploratory_synthetic",
    }
    result["result_digest"] = digest(result)
    return {"run_manifest": run_manifest, "result": result}


def run_matrix(base: dict[str, Any], policies: list[dict[str, Any]],
               seeds: list[int]) -> dict[str, Any]:
    if not isinstance(policies, list) or not policies or not isinstance(seeds, list) or not seeds:
        raise ValueError("run_matrix requires policies and seeds")
    policy_ids = [policy.get("policy_id") for policy in policies if isinstance(policy, dict)]
    if len(policy_ids) != len(policies) or len(set(policy_ids)) != len(policy_ids):
        raise ValueError("policy variants require unique policy_id values")
    if any(type(seed) is not int or seed < 0 or seed > 2**63 - 1 for seed in seeds):
        raise ValueError("seeds must be non-negative 63-bit integers")
    if len(set(seeds)) != len(seeds):
        raise ValueError("seeds must be unique")
    runs = []
    for policy in policies:
        for seed in seeds:
            manifest = dict(base)
            manifest["seed"] = seed
            manifest["policy"] = policy
            runs.append(run_backtest(manifest))
    grouped: dict[str, list[dict[str, Any]]] = {}
    for run in runs:
        grouped.setdefault(run["result"]["policy_id"], []).append(run["result"]["metrics"])
    summary = {}
    for policy_id, metrics in sorted(grouped.items()):
        keys = metrics[0].keys()
        summary[policy_id] = {
            key: sum(float(row[key]) for row in metrics) / len(metrics)
            for key in keys
        }
        summary[policy_id]["replications"] = len(metrics)
    matrix = {
        "matrix_version": "economy-backtest-matrix/v1",
        "simulation_version": SIMULATION_VERSION,
        "runs": runs,
        "summary": summary,
        "verdict": "exploratory_synthetic",
    }
    matrix["matrix_digest"] = digest(matrix)
    return matrix


def write_immutable(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    encoded = canonical(payload) + "\n"
    try:
        with path.open("x", encoding="utf-8") as stream:
            stream.write(encoded)
            stream.flush()
    except FileExistsError:
        if path.read_text(encoding="utf-8") != encoded:
            raise ValueError(f"immutable result collision at {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--manifest", type=Path)
    source.add_argument("--matrix", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/economy-backtests"))
    args = parser.parse_args()
    payload = json.loads((args.manifest or args.matrix).read_text(encoding="utf-8"))
    if args.matrix:
        matrix = run_matrix(payload["base"], payload["policies"], payload["seeds"])
        for run in matrix["runs"]:
            run_id = run["result"]["run_id"]
            write_immutable(args.output_dir / f"{run_id}.manifest.json", run["run_manifest"])
            write_immutable(args.output_dir / f"{run_id}.result.json", run["result"])
        write_immutable(args.output_dir / f"{matrix['matrix_digest']}.matrix.json", matrix)
        print(json.dumps({"matrix_digest": matrix["matrix_digest"],
                          "summary": matrix["summary"]}, indent=2, sort_keys=True))
    else:
        run = run_backtest(payload)
        run_id = run["result"]["run_id"]
        write_immutable(args.output_dir / f"{run_id}.manifest.json", run["run_manifest"])
        write_immutable(args.output_dir / f"{run_id}.result.json", run["result"])
        print(json.dumps({"run_id": run_id, "result_digest": run["result"]["result_digest"],
                          "metrics": run["result"]["metrics"]}, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
