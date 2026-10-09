"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='issue',
    number=1128,
    lane='NEED_EVIDENCE',
    title='deepagent task: verify live worker readiness',
    reasons=('open-task',),
    action='bounded-task-only',
)
