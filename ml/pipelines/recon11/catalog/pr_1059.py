"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1059,
    lane='NEED_EVIDENCE',
    title='test(worktree): regression guard for gh_worktree PR-open invariants',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='test/wt-regression-guard',
)
