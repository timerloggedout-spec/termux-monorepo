"""Pure-Python retrieval metrics for the Pinecone vector-store DoE."""
from __future__ import annotations

import math
import random
from statistics import mean
from typing import Mapping, Sequence


def _dcg(relevances: Sequence[float]) -> float:
    return sum(
        (2.0 ** float(relevance) - 1.0) / math.log2(position + 2.0)
        for position, relevance in enumerate(relevances)
    )


def recall_at_k(ranked_ids: Sequence[str], relevant_ids: Sequence[str], k: int = 5) -> float:
    if k < 1:
        raise ValueError("k must be positive")
    relevant = set(relevant_ids)
    if len(relevant) == 0:
        raise ValueError("relevant_ids must contain at least one chunk ID")
    retrieved = set(ranked_ids[:k])
    return len(retrieved.intersection(relevant)) / len(relevant)


def ndcg_at_k(
    ranked_ids: Sequence[str],
    relevance_by_id: Mapping[str, float],
    k: int = 10,
) -> float:
    if k < 1:
        raise ValueError("k must be positive")
    values = [float(value) for value in relevance_by_id.values()]
    if any(value < 0 for value in values):
        raise ValueError("relevance values must be non-negative")
    ranked = [float(relevance_by_id.get(chunk_id, 0.0)) for chunk_id in ranked_ids[:k]]
    ideal = sorted(values, reverse=True)[:k]
    ideal_dcg = _dcg(ideal)
    if ideal_dcg <= 0:
        raise ValueError("at least one positive relevance grade is required")
    return _dcg(ranked) / ideal_dcg


def mrr_at_k(ranked_ids: Sequence[str], relevant_ids: Sequence[str], k: int = 10) -> float:
    if k < 1:
        raise ValueError("k must be positive")
    relevant = set(relevant_ids)
    if len(relevant) == 0:
        raise ValueError("relevant_ids must contain at least one chunk ID")
    for position, chunk_id in enumerate(ranked_ids[:k], start=1):
        if chunk_id in relevant:
            return 1.0 / position
    return 0.0


def evaluate_arm(
    queries: Sequence[Mapping[str, object]],
    rankings: Mapping[str, Sequence[str]],
    recall_k: int = 5,
    ndcg_k: int = 10,
    mrr_k: int = 10,
) -> dict[str, object]:
    per_query = []
    seen_query_ids = set()
    for query in queries:
        query_id = str(query["query_id"])
        if query_id in seen_query_ids:
            raise ValueError(f"duplicate query_id: {query_id}")
        seen_query_ids.add(query_id)
        ranked_ids = list(rankings[query_id])
        if len(ranked_ids) != len(set(ranked_ids)):
            raise ValueError(f"ranking IDs must be unique for {query_id}")
        relevance = query["relevance_by_chunk_id"]
        if not isinstance(relevance, Mapping):
            raise TypeError(f"relevance_by_chunk_id must be a mapping for {query_id}")
        relevant_ids = [chunk_id for chunk_id, grade in relevance.items() if float(grade) > 0]
        per_query.append({
            "query_id": query_id,
            "recall_at_5": recall_at_k(ranked_ids, relevant_ids, recall_k),
            "ndcg_at_10": ndcg_at_k(ranked_ids, relevance, ndcg_k),
            "mrr_at_10": mrr_at_k(ranked_ids, relevant_ids, mrr_k),
        })
    if len(per_query) == 0:
        raise ValueError("at least one query task is required")
    recall_values = [float(row["recall_at_5"]) for row in per_query]
    ndcg_values = [float(row["ndcg_at_10"]) for row in per_query]
    mrr_values = [float(row["mrr_at_10"]) for row in per_query]
    return {
        "per_query": per_query,
        "per_query_recall_at_5": recall_values,
        "mean_recall_at_5": mean(recall_values),
        "mean_ndcg_at_10": mean(ndcg_values),
        "mean_mrr_at_10": mean(mrr_values),
    }


def paired_bootstrap_ci(
    control_scores: Sequence[float],
    treatment_scores: Sequence[float],
    seed: int = 17,
    resamples: int = 5000,
    confidence: float = 0.95,
) -> dict[str, float | int]:
    if len(control_scores) == 0 or len(control_scores) != len(treatment_scores):
        raise ValueError("paired score arrays require equal positive lengths")
    if resamples < 1 or confidence <= 0.0 or confidence >= 1.0:
        raise ValueError("resamples and confidence must be within their valid ranges")
    differences = [float(t) - float(c) for c, t in zip(control_scores, treatment_scores)]
    if any(math.isfinite(value) is False for value in differences):
        raise ValueError("paired scores must be finite")
    rng = random.Random(seed)
    size = len(differences)
    samples = []
    for _ in range(resamples):
        sampled = [differences[rng.randrange(size)] for _ in range(size)]
        samples.append(mean(sampled))
    samples.sort()
    tail = (1.0 - confidence) / 2.0
    lower_index = min(resamples - 1, max(0, int(math.floor(tail * resamples))))
    upper_index = min(resamples - 1, max(0, int(math.ceil((1.0 - tail) * resamples)) - 1))
    return {
        "mean_difference": mean(differences),
        "ci_lower": samples[lower_index],
        "ci_upper": samples[upper_index],
        "confidence": confidence,
        "resamples": resamples,
    }
