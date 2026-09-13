"""Observe-mode scoring models. Never write, merge, or force-push."""
from .heuristic_scorer import score_pr
from .observe_only import allow_write

__all__ = ["score_pr", "allow_write"]
