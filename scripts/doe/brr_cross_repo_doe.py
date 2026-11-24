#!/usr/bin/env python3
"""Deterministic offline evaluator for the BRR cross-repository DoE campaign.

The evaluator consumes frozen, source-attributed snapshots. It performs no
network access and makes no GitHub or repository mutations.
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import random
import re
import statistics
from pathlib import Path
from typing import Any

CAMPAIGN = "brr-cross-repo-doe"
DATASET_SCHEMA = "brr-cross-repo-doe-dataset/v1"
ARMS = ("lexical", "branch_commit", "context_graph", "fused")
TASK_FAMILIES = {
    "branch_recovery",
    "commit_lineage",
    "regression_context",
    "cross_reference_reconstruction",
}
COVERAGE_STATES = {"COMPLETE", "PARTIAL", "FAILED", "UNVERIFIED"}
SOURCE_KINDS = {
    "brr", "commits", "regressions", "context_graph",
    "cross_plane_graph", "gold_set",
}
DISPOSITIONS = {
    "identical", "behind-only", "ahead-only", "diverged",
    "unresolved-local-ref", "unrelated-or-unavailable-history",
}
REGRESSION_VERDICTS = {
    "green", "regressed", "untestable", "no-benchmark", "unknown",
}
TOKEN_RE = re.compile(r"[a-z0-9]+")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
CASE_ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,79}$")
BOOTSTRAP_REPLICATES = 2000
BOOTSTRAP_SEED = 56402026


def target_identity(repository: str, branch: str, sha: str) -> str:
    """Return the stable repository-qualified identity for a branch tip."""
    return f"{repository}::{branch}@{sha}"


def _is_sha(value: Any) -> bool:
    return isinstance(value, str) and SHA_RE.fullmatch(value) is not None


def _is_https(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("https://")


def _is_timestamp(value: Any) -> bool:
    if not isinstance(value, str):
        return False
    try:
        parsed = dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
        return parsed.tzinfo is not None and parsed.utcoffset() is not None
    except ValueError:
        return False


def _require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def _only_keys(value: dict[str, Any], allowed: set[str], label: str) -> None:
    extra = set(value) - allowed
    _require(not extra, f"{label} contains unsupported fields: {sorted(extra)}")


def validate_dataset(dataset: dict[str, Any]) -> None:
    """Validate the frozen input contract and fail closed on weak evidence."""
    _require(isinstance(dataset, dict), "dataset must be an object")
    _only_keys(dataset, {"schema", "observed_at", "baseline_sha", "candidate_sha", "coverage", "sources", "cases"}, "dataset")
    _require(dataset.get("schema") == DATASET_SCHEMA, "unsupported dataset schema")
    _require(_is_timestamp(dataset.get("observed_at")), "invalid dataset observed_at")
    _require(_is_sha(dataset.get("baseline_sha")), "baseline_sha must be 40 lowercase hex")
    _require(_is_sha(dataset.get("candidate_sha")), "candidate_sha must be 40 lowercase hex")

    coverage = dataset.get("coverage")
    _require(isinstance(coverage, dict), "coverage must be an object")
    _only_keys(coverage, {"state", "repositories", "next_page"}, "coverage")
    coverage_state = coverage.get("state")
    _require(coverage_state in COVERAGE_STATES, "invalid coverage state")
    repositories = coverage.get("repositories")
    _require(
        isinstance(repositories, list) and repositories
        and all(isinstance(repo, str) and "/" in repo for repo in repositories),
        "coverage.repositories must list owner/repository identities",
    )
    _require(len(set(repositories)) == len(repositories), "duplicate coverage repository")
    next_page = coverage.get("next_page")
    _require(next_page is None or (type(next_page) is int and next_page >= 1),
             "coverage.next_page must be null or a positive integer")
    if coverage_state == "COMPLETE":
        _require(next_page is None, "complete coverage requires next_page=null")

    sources = dataset.get("sources")
    _require(isinstance(sources, list) and sources, "sources must be a non-empty list")
    sourced_repositories: set[str] = set()
    source_pairs: set[tuple[str, str]] = set()
    source_kinds: set[str] = set()
    for source in sources:
        _require(isinstance(source, dict), "source entry must be an object")
        _only_keys(source, {"kind", "repository", "sha", "observed_at", "coverage", "url"}, "source")
        _require(source.get("kind") in SOURCE_KINDS, "invalid source kind")
        _require(source.get("repository") in repositories, "source repository outside coverage")
        sourced_repositories.add(source["repository"])
        source_pairs.add((source["kind"], source["repository"]))
        source_kinds.add(source["kind"])
        _require(_is_sha(source.get("sha")), "source sha must be 40 lowercase hex")
        _require(_is_timestamp(source.get("observed_at")), "invalid source observed_at")
        _require(source.get("coverage") in COVERAGE_STATES, "invalid source coverage")
        _require(_is_https(source.get("url")), "source URL must use HTTPS")
        if coverage_state == "COMPLETE":
            _require(source["coverage"] == "COMPLETE",
                     "complete dataset requires complete source coverage")

    _require(set(repositories).issubset(sourced_repositories),
             "every covered repository needs at least one source receipt")
    _require(all((kind, repo) in source_pairs
                 for repo in repositories for kind in ("brr", "commits")),
             "every covered repository needs BRR and commit source receipts")
    _require({"regressions", "gold_set"}.issubset(source_kinds),
             "regression and adjudicated gold-set source receipts are required")
    _require(bool({"context_graph", "cross_plane_graph"} & source_kinds),
             "at least one context or cross-plane graph source is required")

    cases = dataset.get("cases")
    _require(isinstance(cases, list) and cases, "cases must be a non-empty list")
    case_ids: set[str] = set()
    for case in cases:
        _require(isinstance(case, dict), "case entry must be an object")
        _only_keys(case, {"case_id", "task_family", "query", "gold_target_ids", "candidates"}, "case")
        case_id = case.get("case_id")
        _require(isinstance(case_id, str) and CASE_ID_RE.fullmatch(case_id), "case_id must be a safe slug (1-80 characters)")
        _require(case_id not in case_ids, "duplicate case_id")
        case_ids.add(case_id)
        _require(case.get("task_family") in TASK_FAMILIES, "invalid task_family")
        _require(isinstance(case.get("query"), str) and case["query"].strip(),
                 "query must be non-empty")
        gold = case.get("gold_target_ids")
        _require(isinstance(gold, list) and gold, "gold_target_ids must be non-empty")
        _require(len(set(gold)) == len(gold), "duplicate gold target id")

        candidates = case.get("candidates")
        _require(isinstance(candidates, list) and candidates, "candidates must be non-empty")
        candidate_ids: set[str] = set()
        verified_ids: set[str] = set()
        for candidate in candidates:
            _require(isinstance(candidate, dict), "candidate must be an object")
            _only_keys(candidate, {"target_id", "repository", "branch", "sha", "evidence_status", "disposition", "ahead_of_default", "behind_default", "unique_commit_count", "pr_state", "regression_verdict", "title", "commit_subjects", "commit_shas", "pull_request_numbers", "issue_numbers", "regression_reason", "graph_edges", "evidence_refs"}, "candidate")
            repository = candidate.get("repository")
            branch = candidate.get("branch")
            sha = candidate.get("sha")
            _require(repository in repositories, "candidate repository outside coverage")
            _require(isinstance(branch, str) and branch, "candidate branch is required")
            _require(_is_sha(sha), "candidate sha must be 40 lowercase hex")
            expected_id = target_identity(repository, branch, sha)
            _require(candidate.get("target_id") == expected_id,
                     "target_id must equal owner/repository::branch@full_sha")
            target_id = candidate["target_id"]
            _require(target_id not in candidate_ids, "duplicate candidate target_id")
            candidate_ids.add(target_id)
            evidence_status = candidate.get("evidence_status")
            _require(evidence_status in {"verified", "candidate"},
                     "evidence_status must be verified or candidate")
            if evidence_status == "verified":
                verified_ids.add(target_id)
            _require(candidate.get("disposition") in DISPOSITIONS,
                     "invalid BRR disposition")
            for field in ("ahead_of_default", "behind_default", "unique_commit_count"):
                value = candidate.get(field)
                _require(value is None or (type(value) is int and value >= 0),
                         f"{field} must be a non-negative integer or null")
            _require(candidate.get("pr_state") in {"open", "closed", "merged", "none", "unknown"},
                     "invalid pr_state")
            verdict = candidate.get("regression_verdict")
            _require(verdict in REGRESSION_VERDICTS, "invalid regression_verdict")
            regression_reason = candidate.get("regression_reason")
            _require(regression_reason is None or isinstance(regression_reason, str),
                     "regression_reason must be text or null")
            if verdict in {"untestable", "no-benchmark"}:
                _require(isinstance(regression_reason, str) and regression_reason.strip(),
                         "untestable/no-benchmark verdicts require a reason")
            commit_shas = candidate.get("commit_shas")
            _require(isinstance(commit_shas, list) and all(_is_sha(sha) for sha in commit_shas),
                     "commit_shas must be a list of full commit SHAs")
            _require(len(set(commit_shas)) == len(commit_shas),
                     "commit_shas must be unique")
            commit_count = candidate.get("unique_commit_count")
            if commit_count is not None:
                _require(commit_count == len(commit_shas),
                         "unique_commit_count must match the complete commit_shas list")
            for field in ("pull_request_numbers", "issue_numbers"):
                numbers = candidate.get(field)
                _require(isinstance(numbers, list)
                         and all(type(number) is int and number >= 1 for number in numbers),
                         f"{field} must be a list of positive integers")
            _require(isinstance(candidate.get("title"), str), "candidate title must be text")
            subjects = candidate.get("commit_subjects")
            _require(isinstance(subjects, list) and all(isinstance(x, str) for x in subjects),
                     "commit_subjects must be a string list")
            edges = candidate.get("graph_edges")
            _require(isinstance(edges, list), "graph_edges must be a list")
            for edge in edges:
                _require(isinstance(edge, dict), "graph edge must be an object")
                _only_keys(edge, {"relationship", "confidence", "evidence_ref"}, "graph edge")
                _require(isinstance(edge.get("relationship"), str) and edge["relationship"],
                         "graph relationship is required")
                _require(edge.get("confidence") in {"verified", "candidate"},
                         "invalid graph edge confidence")
                _require(_is_https(edge.get("evidence_ref")),
                         "graph edge evidence_ref must use HTTPS")
            refs = candidate.get("evidence_refs")
            _require(isinstance(refs, list) and refs, "candidate needs evidence_refs")
            _require(all(_is_https(ref) for ref in refs),
                     "candidate evidence_refs must use HTTPS")
        _require(set(gold).issubset(verified_ids),
                 "gold targets must resolve to verified candidates")


def regression_signal(candidate: dict[str, Any]) -> float:
    """Return the preregistered regression relevance signal."""
    return {
        "regressed": 1.0,
        "untestable": 0.5,
        "no-benchmark": 0.25,
        "green": 0.0,
        "unknown": 0.0,
    }[candidate["regression_verdict"]]


def _lexical_signal(candidate: dict[str, Any], query: str) -> float:
    query_tokens = set(TOKEN_RE.findall(query.lower()))
    if not query_tokens:
        return 0.0
    text = " ".join([
        candidate["repository"],
        candidate["branch"],
        candidate["title"],
        *candidate["commit_subjects"],
        *[f"pr {number}" for number in candidate["pull_request_numbers"]],
        *[f"issue {number}" for number in candidate["issue_numbers"]],
    ]).lower()
    present = set(TOKEN_RE.findall(text))
    return len(query_tokens & present) / len(query_tokens)


def _branch_commit_signal(candidate: dict[str, Any]) -> float:
    disposition = candidate["disposition"]
    branch_signal = 1.0 if disposition in {"ahead-only", "diverged"} else 0.0
    pr_signal = 1.0 if candidate["pr_state"] == "open" else 0.0
    brr_signal = 0.7 * branch_signal + 0.3 * pr_signal
    commits = candidate["unique_commit_count"]
    commit_signal = min(commits, 5) / 5 if commits is not None else 0.0
    return 0.6 * brr_signal + 0.4 * commit_signal


def _graph_signal(candidate: dict[str, Any]) -> float:
    verified_edges = sum(
        1 for edge in candidate["graph_edges"] if edge["confidence"] == "verified"
    )
    return min(verified_edges, 4) / 4


def score_candidate(candidate: dict[str, Any], query: str, arm: str) -> float:
    """Score one verified target under one preregistered retrieval arm."""
    if candidate.get("evidence_status") != "verified":
        return 0.0
    lexical = _lexical_signal(candidate, query)
    branch_commit = _branch_commit_signal(candidate)
    graph = _graph_signal(candidate)
    regression = regression_signal(candidate)
    if arm == "lexical":
        return lexical
    if arm == "branch_commit":
        return branch_commit
    if arm == "context_graph":
        return graph
    if arm == "fused":
        return statistics.mean((lexical, branch_commit, graph, regression))
    raise ValueError(f"unknown retrieval arm: {arm}")


def _case_metrics(ranked_ids: list[str], gold_ids: list[str], k: int = 5) -> dict[str, float]:
    top = ranked_ids[:k]
    hits = sum(1 for target_id in top if target_id in set(gold_ids))
    precision = hits / min(k, len(ranked_ids)) if ranked_ids else 0.0
    recall = hits / len(gold_ids) if gold_ids else 0.0
    f1 = (2 * precision * recall / (precision + recall)
          if precision + recall else 0.0)
    reciprocal_rank = 0.0
    for rank, target_id in enumerate(ranked_ids, start=1):
        if target_id in gold_ids:
            reciprocal_rank = 1.0 / rank
            break
    return {
        "precision_at_5": precision,
        "recall_at_5": recall,
        "f1_at_5": f1,
        "mean_reciprocal_rank": reciprocal_rank,
    }


def _percentile(values: list[float], fraction: float) -> float:
    ordered = sorted(values)
    if len(ordered) == 1:
        return ordered[0]
    position = (len(ordered) - 1) * fraction
    lower = int(position)
    upper = min(lower + 1, len(ordered) - 1)
    weight = position - lower
    return ordered[lower] * (1 - weight) + ordered[upper] * weight


def _decision(cases: list[dict[str, Any]], dataset: dict[str, Any],
              summaries: dict[str, dict[str, float]]) -> dict[str, Any]:
    single_arms = ("lexical", "branch_commit", "context_graph")
    best_arm = max(single_arms, key=lambda arm: summaries[arm]["f1_at_5"])
    by_case: dict[str, dict[str, float]] = {}
    for row in cases:
        by_case.setdefault(row["case_id"], {})[row["arm"]] = row["metrics"]["f1_at_5"]
    differences = [
        arms["fused"] - arms[best_arm]
        for arms in by_case.values()
        if "fused" in arms and best_arm in arms
    ]
    mean_difference = statistics.mean(differences) if differences else 0.0
    rng = random.Random(BOOTSTRAP_SEED)
    bootstrap_means = []
    if differences:
        for _ in range(BOOTSTRAP_REPLICATES):
            sample = [differences[rng.randrange(len(differences))]
                      for _ in range(len(differences))]
            bootstrap_means.append(statistics.mean(sample))
    interval = (
        [_percentile(bootstrap_means, 0.025), _percentile(bootstrap_means, 0.975)]
        if bootstrap_means else [0.0, 0.0]
    )
    repositories = {
        target_id.split("::", 1)[0]
        for case in dataset["cases"]
        for target_id in case["gold_target_ids"]
    }
    task_families = {case["task_family"] for case in dataset["cases"]}
    sample_met = len(dataset["cases"]) >= 30 and len(repositories) >= 3 and len(task_families) >= 3
    coverage_complete = dataset["coverage"]["state"] == "COMPLETE"
    precision_guard = summaries["fused"]["precision_at_5"] >= summaries[best_arm]["precision_at_5"]
    reasons = []
    if not sample_met:
        reasons.append("confirmatory_sample_requirement_unmet")
    if not coverage_complete:
        reasons.append("source_coverage_incomplete")
    if mean_difference < 0.05:
        reasons.append("absolute_f1_improvement_below_0.05")
    if interval[0] <= 0:
        reasons.append("paired_bootstrap_lower_bound_not_above_zero")
    if not precision_guard:
        reasons.append("verified_precision_guard_failed")
    return {
        "best_single_source_arm": best_arm,
        "mean_f1_improvement": mean_difference,
        "paired_bootstrap_95_percentile_interval": interval,
        "bootstrap_replicates": BOOTSTRAP_REPLICATES,
        "confirmatory_sample_met": sample_met,
        "coverage_complete": coverage_complete,
        "verified_precision_guard": precision_guard,
        "champion_candidate": not reasons,
        "reasons": reasons,
    }


def evaluate_dataset(dataset: dict[str, Any]) -> dict[str, Any]:
    """Evaluate all cases under all four arms using a frozen dataset."""
    validate_dataset(dataset)
    result_cases: list[dict[str, Any]] = []
    for case in dataset["cases"]:
        verified = [
            row for row in case["candidates"]
            if row["evidence_status"] == "verified"
        ]
        candidate_only = sorted(
            row["target_id"] for row in case["candidates"]
            if row["evidence_status"] == "candidate"
        )
        candidate_edge_ids = sorted(
            row["target_id"] for row in verified
            if any(edge["confidence"] == "candidate" for edge in row["graph_edges"])
        )
        assignment_order = _assignment_order(case["case_id"])
        for arm in assignment_order:
            scored = [
                (score_candidate(row, case["query"], arm), row["target_id"])
                for row in verified
            ]
            ranked_ids = [
                target_id for _, target_id in sorted(
                    scored, key=lambda pair: (-pair[0], pair[1])
                )
            ]
            result_cases.append({
                "case_id": case["case_id"],
                "task_family": case["task_family"],
                "arm": arm,
                "assignment_order": assignment_order,
                "ranked_target_ids": ranked_ids,
                "candidate_only_ids": candidate_only,
                "candidate_edge_ids": candidate_edge_ids,
                "evidence_refs": sorted({
                    ref
                    for candidate in case["candidates"]
                    if candidate["target_id"] in set(ranked_ids[:5]) | set(candidate_only)
                    for ref in (
                        candidate["evidence_refs"]
                        + [edge["evidence_ref"] for edge in candidate["graph_edges"]]
                    )
                }),
                "metrics": {
                    **_case_metrics(ranked_ids, case["gold_target_ids"]),
                    "untestable_fraction": (
                        sum(1 for row in verified
                            if row["regression_verdict"] in {"untestable", "no-benchmark", "unknown"})
                        / len(verified) if verified else 0.0
                    ),
                    "unresolved_fraction": (
                        sum(1 for row in verified
                            if row["disposition"] in {"unresolved-local-ref", "unrelated-or-unavailable-history"})
                        / len(verified) if verified else 0.0
                    ),
                },
            })

    summaries: dict[str, dict[str, float]] = {}
    for arm in ARMS:
        rows = [row for row in result_cases if row["arm"] == arm]
        summaries[arm] = {
            metric: statistics.mean(row["metrics"][metric] for row in rows)
            for metric in (
                "precision_at_5", "recall_at_5", "f1_at_5",
                "mean_reciprocal_rank", "untestable_fraction", "unresolved_fraction",
            )
        }
        summaries[arm]["candidate_only_leads"] = float(
            sum(len(row["candidate_only_ids"]) for row in rows)
        )
    return {
        "schema": "brr-cross-repo-doe-results/v1",
        "campaign_id": CAMPAIGN,
        "observed_at": dataset["observed_at"],
        "baseline_sha": dataset["baseline_sha"],
        "candidate_sha": dataset["candidate_sha"],
        "coverage_state": dataset["coverage"]["state"],
        "complete_source_coverage_rate": 1.0 if dataset["coverage"]["state"] == "COMPLETE" else 0.0,
        "repositories": sorted(dataset["coverage"]["repositories"]),
        "query_count": len(dataset["cases"]),
        "task_families": sorted({case["task_family"] for case in dataset["cases"]}),
        "sources": dataset["sources"],
        "arms": summaries,
        "decision": _decision(result_cases, dataset, summaries),
        "cases": result_cases,
    }


def build_experiment_records(result: dict[str, Any], baseline_sha: str,
                             candidate_sha: str, observed_at: str) -> list[dict[str, Any]]:
    """Create canonical DoE-family records: one record per query x arm."""
    _require(_is_sha(baseline_sha), "baseline_sha must be 40 lowercase hex")
    _require(_is_sha(candidate_sha), "candidate_sha must be 40 lowercase hex")
    _require(_is_timestamp(observed_at), "observed_at must be an ISO timestamp")
    source_refs = [source["url"] for source in result["sources"]]
    records = []
    for row in result["cases"]:
        metrics = row["metrics"]
        evidence_refs = set(source_refs)
        evidence_refs.update(row["evidence_refs"])
        records.append({
            "schema_version": "1.0",
            "experiment_id": f"{CAMPAIGN}-{row['case_id']}-{row['arm']}",
            "observed_at": observed_at,
            "baseline_sha": baseline_sha,
            "candidate_sha": candidate_sha,
            "suite": f"doe-family:{CAMPAIGN}",
            "cohort": row["task_family"],
            "treatment": {
                "manager_policy_id": f"{CAMPAIGN}/v1",
                "arm": row["arm"],
                "instance": None,
            },
            "status": "observed" if result["coverage_state"] == "COMPLETE" else "blocked",
            "outcome": "measured" if result["coverage_state"] == "COMPLETE"
                       else "partial_coverage",
            "metrics": {
                "precision_at_5": metrics["precision_at_5"],
                "recall_at_5": metrics["recall_at_5"],
                "f1_at_5": metrics["f1_at_5"],
                "mean_reciprocal_rank": metrics["mean_reciprocal_rank"],
                "candidate_only_leads": len(row["candidate_only_ids"]),
                "untestable_fraction": metrics["untestable_fraction"],
                "unresolved_fraction": metrics["unresolved_fraction"],
            },
            "provenance": "github",
            "confidence": "high" if result["coverage_state"] == "COMPLETE" else "low",
            "evidence_refs": sorted(evidence_refs),
        })
    return records


def _assignment_order(case_id: str) -> list[str]:
    """Stable per-case randomized order; result tables remain arm-keyed."""
    digest = hashlib.sha256(case_id.encode("utf-8")).digest()
    seed = BOOTSTRAP_SEED ^ int.from_bytes(digest[:8], "big")
    arms = list(ARMS)
    random.Random(seed).shuffle(arms)
    return arms


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--summary", required=True, type=Path)
    args = parser.parse_args()

    dataset = json.loads(args.dataset.read_text(encoding="utf-8"))
    result = evaluate_dataset(dataset)
    records = build_experiment_records(
        result,
        dataset["baseline_sha"],
        dataset["candidate_sha"],
        dataset["observed_at"],
    )
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for record in records:
        path = args.output_dir / f"{record['experiment_id']}.json"
        path.write_text(json.dumps(record, indent=2, sort_keys=True) + "\n",
                        encoding="utf-8")
    args.summary.parent.mkdir(parents=True, exist_ok=True)
    args.summary.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n",
                            encoding="utf-8")
    print(
        f"evaluated {result['query_count']} queries across {len(ARMS)} arms; "
        f"wrote {len(records)} records; coverage={result['coverage_state']}; "
        f"champion_candidate={result['decision']['champion_candidate']}"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
