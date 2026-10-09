"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=540,
    lane='CANDIDATE',
    title='docs+ops: fail-closed image asset pipeline + ATES',
    reasons=('state:unknown',),
    action='dual-gate-before-promote',
    base='master',
)
