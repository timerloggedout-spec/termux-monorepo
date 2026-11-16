"""Frozen recon09 observation. Not a merge decision. Issue #175 / 2026-10-11."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1063,
    lane='NEED_EVIDENCE',
    title='fix(preflight): guard score() against omitted env (KILL_AGENT nil-env crash)',
    reasons=('wrong-base:feat/dashboard-lanes-v2',),
    action='never-retarget',
    base='feat/dashboard-lanes-v2',
    login='timerloggedout-spec',
    head_ref='fix/preflight-env-none-guard-v3',
)
