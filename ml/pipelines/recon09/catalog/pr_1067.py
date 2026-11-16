"""Frozen recon09 observation. Not a merge decision. Issue #175 / 2026-10-11."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1067,
    lane='NEED_EVIDENCE',
    title='fix(gh_worktree): persist branch->base on create (correct PR base)',
    reasons=('wrong-base:feat/dashboard-lanes-v2',),
    action='never-retarget',
    base='feat/dashboard-lanes-v2',
    login='timerloggedout-spec',
    head_ref='fix/wt-create-persist-base-v2',
)
