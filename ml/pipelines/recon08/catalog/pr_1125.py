"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1125,
    lane='NEED_EVIDENCE',
    title='feat(ates): deterministic orchestrator recon + DoE/MVT benchmark lane',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/ates-orchestrator-recon-doe-mvt-dspy',
)
