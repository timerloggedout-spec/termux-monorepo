"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=714,
    lane='NEED_EVIDENCE',
    title='feat(ops): stepie-stepwise-ops skill — production planning surface (Stepie MCP)',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/stepie-stepwise-ops-skill-20260921',
)
