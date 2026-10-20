"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=806,
    lane='NEED_EVIDENCE',
    title='ops: harden evaluation lanes and GitHub App capability evidence',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/production-steward-20260924',
)
