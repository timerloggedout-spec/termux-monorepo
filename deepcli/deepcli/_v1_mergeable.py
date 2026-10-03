"""_v1_mergeable - decide if a PR status rollup is safe to auto-merge.

Revision 2: PENDING/EXPECTED/IN_PROGRESS states now block (previously
only None or an explicit FAIL set did). Anything not positively PASSING
and not explicitly SKIPPED is treated as a blocker.

Motivation
----------
The continuous-improvement loop kept producing green, MERGEABLE PRs
(1015-1032) that never merged because the Vercel preview-deploy
StatusContexts FAIL (rate-limit) while every real check is SUCCESS.
This module answers: "given this PR's statusCheckRollup, is it safe to
merge now?" It ignores a small allowlist of non-gating contexts and
requires everything else to be terminal-green.

Public API:
    is_merge_ready(rollup, ignore=IGNORED_CONTEXTS) -> bool
    merge_blockers(rollup, ignore=IGNORED_CONTEXTS) -> list[str]
    IGNORED_CONTEXTS                                  -> frozenset[str]

Stdlib only. No network. No deepcli dependencies.
"""

__all__ = ["is_merge_ready", "merge_blockers", "IGNORED_CONTEXTS"]

# Informational contexts that must never block a merge (matched as a
# case-insensitive PREFIX of the context name).
IGNORED_CONTEXTS = frozenset(
    {
        "vercel",  # preview deploys; rate-limited, non-gating
        "mintlify",  # docs preview; always SKIPPED
        "vercel preview",  # "Vercel Preview Comments" status
    }
)

# Conclusions that mean "done and passing".
_PASS = frozenset({"SUCCESS", "NEUTRAL"})

# Conclusions that mean "done but intentionally skipped" - neutral.
_SKIP = frozenset({"SKIPPED"})


def _name_of(entry):
    """Best-effort display name for a rollup entry (name or context)."""
    if not isinstance(entry, dict):
        return ""
    for key in ("name", "context"):
        v = entry.get(key)
        if isinstance(v, str) and v:
            return v
    return ""


def _is_ignored(name, ignore):
    if not name:
        return False
    low = name.lower()
    return any(low.startswith(p.lower()) for p in ignore)


def _conclusion_of(entry):
    """Normalized conclusion/state, or None if the entry has neither."""
    if not isinstance(entry, dict):
        return None
    for key in ("conclusion", "state"):
        v = entry.get(key)
        if isinstance(v, str) and v:
            return v.upper()
    return None


def merge_blockers(rollup, ignore=IGNORED_CONTEXTS):
    """Return the list of context names that currently block a merge.

    Empty list => safe to merge. A non-ignored context blocks unless it
    is positively PASSING (SUCCESS/NEUTRAL) or explicitly SKIPPED. Thus
    FAILURE, TIMED_OUT, CANCELLED, PENDING, EXPECTED, IN_PROGRESS and
    missing-conclusion entries all block. Malformed entries are ignored.
    """
    blockers = []
    if not isinstance(rollup, (list, tuple)):
        return ["<malformed rollup>"]
    for entry in rollup:
        if not isinstance(entry, dict):
            continue
        name = _name_of(entry)
        if _is_ignored(name, ignore):
            continue
        concl = _conclusion_of(entry)
        if concl in _PASS or concl in _SKIP:
            continue
        blockers.append(name or "<pending>")
    return blockers


def is_merge_ready(rollup, ignore=IGNORED_CONTEXTS):
    """True iff no non-ignored context blocks the merge."""
    return not merge_blockers(rollup, ignore=ignore)
