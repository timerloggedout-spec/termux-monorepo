"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=1128,
    lane='NEED_EVIDENCE',
    title='deepagent task: verify live worker readiness',
    reasons=('open-task',),
    action='bounded-task-only',
)
