"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=175,
    lane='CANDIDATE',
    title='ops: OPERATOR priority matrix + master functional gate (live 2026-09-29)',
    reasons=('hub-not-comment-stream',),
    action='edit-body-do-not-pulse',
)
