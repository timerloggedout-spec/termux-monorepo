"""Frozen recon09 observation. Not a merge decision. Issue #175 / 2026-10-11."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1075,
    lane='NEED_EVIDENCE',
    title='docs(preflight): drop phantom check_action entry + add docstring/API-drift guard test',
    reasons=('wrong-base:feat/dashboard-lanes-v2',),
    action='never-retarget',
    base='feat/dashboard-lanes-v2',
    login='timerloggedout-spec',
    head_ref='docs/preflight-remove-phantom-check-action',
)
