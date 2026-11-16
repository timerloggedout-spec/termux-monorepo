"""Frozen recon09 observation. Not a merge decision. Issue #175 / 2026-10-11."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1201,
    lane='NEED_EVIDENCE',
    title='ops(queue-v3 + recon): inventory retry logging + 2026-10-10 evidence note',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/workflow-hygiene-accel-20261010',
)
