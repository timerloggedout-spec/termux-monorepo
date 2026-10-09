"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='issue',
    number=1026,
    lane='NEED_EVIDENCE',
    title='[Actions Incident] Agent Throughput Evidence: failure',
    reasons=('actions-incident',),
    action='evidence-not-a-gate',
)
