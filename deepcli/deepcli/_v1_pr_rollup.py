"""_v1_pr_rollup — pure-function PR triage/merge classifier.

Motivation
----------
The agent routinely accumulates dozens of open PRs (test coverage, small
fixes, feature branches) with no automated way to decide which are safe to
land and in what order.  Manual review does not scale and stale PRs rot,
creating rebase churn.

This module implements a *pure, offline, dependency-free* classifier:
given a PR's metadata (mergeable state, CI rollup, age, size, review state,
draft flag), it returns a bucket plus a human-readable rationale.

Buckets (ordered by actionability)
---------------------------------
- ``merge``     — safe to merge now (green CI, clean merge, reviewed/trivial)
- ``rebase``    — content is fine but the branch is behind / has conflicts
- ``recheck``   — CI pending or unknown; retry later, do not act yet
- ``needs_work``— failing CI, requested changes, or conflicts needing a human
- ``skip``      — draft, very fresh, or explicitly blocked

The classifier is intentionally conservative: anything ambiguous lands in
``recheck`` or ``needs_work`` rather than ``merge``.  The invariant is
that **no PR is ever classified ``merge`` unless every gate passes**.
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Iterable, Mapping, Sequence

__all__ = [
    "PRSignals",
    "Classification",
    "classify",
    "rollup",
    "BUCKET_ORDER",
]

# Canonical bucket ordering, most-actionable first.
BUCKET_ORDER = ("merge", "rebase", "recheck", "needs_work", "skip")

# CI states that count as definitively green / red.
_GREEN = {"success", "passing", "passed", "green", "ok"}
_RED = {
    "failure",
    "failing",
    "failed",
    "error",
    "red",
    "cancelled",
    "timed_out",
    "action_required",
}
_PENDING = {
    "pending",
    "queued",
    "in_progress",
    "waiting",
    "expected",
    "neutral",
    "stale",
}

# Mergeable states (GitHub GraphQL `mergeable`).
_MERGEABLE_OK = {"mergeable", "clean", "has_hooks", "unstable"}
_MERGEABLE_BAD = {"conflicting", "dirty"}
_MERGEABLE_UNKNOWN = {"unknown", ""}


def _norm(s: Any) -> str:
    """Lower-case, strip, and map None to the empty string."""
    if s is None:
        return ""
    return str(s).strip().lower()


def _coerce_bool(v: Any) -> bool:
    """Tolerant bool coercion: accepts bool, 0/1, 'true'/'yes'/'1'."""
    if isinstance(v, bool):
        return v
    if isinstance(v, (int, float)):
        return v != 0
    return _norm(v) in {"1", "true", "yes", "y", "on"}


def _coerce_int(v: Any, default: int = 0) -> int:
    try:
        return int(v)
    except (TypeError, ValueError):
        return default


@dataclass(frozen=True)
class PRSignals:
    """Normalized, transport-agnostic view of a single PR.

    Build one of these from `gh pr view --json ...` output via
    :meth:`from_gh`.  All fields have conservative defaults so partial
    metadata never crashes the classifier — it just falls back to
    ``recheck``.
    """

    number: int = 0
    title: str = ""
    draft: bool = False
    mergeable: str = "unknown"  # mergeable | conflicting | unknown
    merge_state: str = ""  # clean | behind | dirty | blocked | ...
    ci_state: str = "unknown"  # success | failure | pending | unknown
    ci_failing: int = 0  # count of failing checks
    ci_pending: int = 0  # count of pending checks
    review_decision: str = ""  # approved | changes_requested | review_required | ""
    additions: int = 0
    deletions: int = 0
    changed_files: int = 0
    age_hours: float = 0.0
    comments: int = 0

    @property
    def churn(self) -> int:
        return self.additions + self.deletions

    @classmethod
    def from_gh(cls, data: Mapping[str, Any]) -> "PRSignals":
        """Build signals from a `gh pr view --json` payload.

        Recognized keys (all optional): number, title, isDraft,
        mergeable, mergeStateStatus, statusCheckRollup (list of
        {conclusion,state,status}), reviewDecision, additions, deletions,
        changedFiles, createdAt/ageHours, comments (list or int).
        """
        checks: Sequence[Mapping[str, Any]] = data.get("statusCheckRollup") or []
        ci_failing = ci_pending = 0
        saw_success = False
        saw_any = False
        for chk in checks:
            if not isinstance(chk, Mapping):
                continue
            saw_any = True
            # GitHub check-runs use `conclusion`/`status`; status contexts
            # use `state`. Collapse to one token.
            token = _norm(
                chk.get("conclusion") or chk.get("state") or chk.get("status")
            )
            if token in _RED:
                ci_failing += 1
            elif token in _PENDING:
                ci_pending += 1
            elif token in _GREEN:
                saw_success = True

        if ci_failing:
            ci_state = "failure"
        elif ci_pending:
            ci_state = "pending"
        elif saw_success or (saw_any and not ci_failing and not ci_pending):
            ci_state = "success"
        else:
            ci_state = "unknown"

        comments = data.get("comments")
        if isinstance(comments, Sequence) and not isinstance(comments, (str, bytes)):
            n_comments = len(comments)
        else:
            n_comments = _coerce_int(comments, 0)

        return cls(
            number=_coerce_int(data.get("number"), 0),
            title=str(data.get("title") or ""),
            draft=_coerce_bool(data.get("isDraft")),
            mergeable=_norm(data.get("mergeable")) or "unknown",
            merge_state=_norm(data.get("mergeStateStatus")),
            ci_state=ci_state,
            ci_failing=ci_failing,
            ci_pending=ci_pending,
            review_decision=_norm(data.get("reviewDecision")),
            additions=_coerce_int(data.get("additions"), 0),
            deletions=_coerce_int(data.get("deletions"), 0),
            changed_files=_coerce_int(data.get("changedFiles"), 0),
            age_hours=float(data.get("ageHours") or 0.0),
            comments=n_comments,
        )


@dataclass(frozen=True)
class Classification:
    """Result of classifying one PR."""

    number: int
    bucket: str
    reasons: tuple[str, ...] = field(default_factory=tuple)

    @property
    def actionable(self) -> bool:
        return self.bucket in ("merge", "rebase")

    def to_dict(self) -> dict:
        d = asdict(self)
        d["reasons"] = list(self.reasons)
        d["actionable"] = self.actionable
        return d


def classify(sig: PRSignals) -> Classification:
    """Classify a single PR into exactly one bucket.

    Precedence (first match wins):

    1. draft / explicitly blocked          -> skip
    2. conflicting mergeable state         -> needs_work
    3. failing CI                          -> needs_work
    4. changes_requested                   -> needs_work
    5. non-clean merge_state (behind/…)    -> rebase
    6. pending / unknown CI, unknown merge -> recheck
    7. no review + non-trivial churn       -> recheck (needs review)
    8. otherwise                           -> merge
    """
    reasons: list[str] = []

    if sig.draft:
        return Classification(sig.number, "skip", ("draft PR",))

    mergeable = _norm(sig.mergeable)
    merge_state = _norm(sig.merge_state)
    review = _norm(sig.review_decision)

    if mergeable in _MERGEABLE_BAD or merge_state in {"dirty", "conflicting"}:
        return Classification(sig.number, "needs_work", ("merge conflict",))

    if _norm(sig.ci_state) == "failure" or sig.ci_failing > 0:
        reasons.append(
            f"ci failing ({sig.ci_failing} check(s))"
            if sig.ci_failing
            else "ci failing"
        )
        return Classification(sig.number, "needs_work", tuple(reasons))

    if review == "changes_requested":
        return Classification(sig.number, "needs_work", ("changes requested",))

    # Branch is behind base or otherwise non-clean -> rebase first.
    if merge_state in {"behind", "out_of_date", "non_fast_forward"}:
        return Classification(sig.number, "rebase", (f"merge state {merge_state}",))

    if _norm(sig.ci_state) in ("pending", "unknown") or sig.ci_pending > 0:
        return Classification(
            sig.number, "recheck", (f"ci {_norm(sig.ci_state) or 'unknown'}",)
        )

    if mergeable in _MERGEABLE_UNKNOWN:
        return Classification(sig.number, "recheck", ("mergeability unknown",))

    # Conservative merge gate: require approval OR trivially small diff.
    trivial = sig.churn <= 20 and sig.changed_files <= 3
    if review != "approved" and not trivial:
        return Classification(
            sig.number,
            "recheck",
            (f"needs review (churn={sig.churn}, files={sig.changed_files})",),
        )

    if review == "approved":
        reasons.append("approved")
    if trivial:
        reasons.append("trivial diff")
    if merge_state == "clean":
        reasons.append("merge state clean")
    reasons.append("ci success")
    return Classification(sig.number, "merge", tuple(reasons))


def rollup(signals: Iterable[PRSignals]) -> dict:
    """Group many PRs into an ordered, de-duplicated action plan.

    Returns::

        {
          "buckets": {bucket: [Classification.to_dict(), ...]},
          "counts":  {bucket: n},
          "actionable": [numbers...],   # merge-then-rebase, in order
        }

    Invariant: every input signal appears exactly once across all buckets.
    """
    buckets: dict[str, list] = {b: [] for b in BUCKET_ORDER}
    seen: set[int] = set()
    for sig in signals:
        c = classify(sig)
        if c.number in seen and c.number != 0:
            # Duplicate PR number: keep the first (stable), note it.
            continue
        seen.add(c.number)
        buckets[c.bucket].append(c.to_dict())

    counts = {b: len(buckets[b]) for b in BUCKET_ORDER}
    actionable: list[int] = []
    for b in ("merge", "rebase"):
        actionable.extend(x["number"] for x in buckets[b] if x["number"])

    return {"buckets": buckets, "counts": counts, "actionable": actionable}
