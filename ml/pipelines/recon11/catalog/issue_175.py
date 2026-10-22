"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=175,
    lane='CANDIDATE',
    title='ops: OPERATOR priority matrix + master functional gate',
    reasons=('hub',),
    action='edit-body-when-intent-changes',
    base='',
    login='',
    head_ref='',
)
