"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1057,
    lane='NEED_EVIDENCE',
    title='fix(preflight): implement documented check_action() (docstring/API drift)',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='fix/preflight-check-action-impl',
)
