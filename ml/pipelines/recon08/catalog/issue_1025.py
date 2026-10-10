"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=1025,
    lane='NEED_EVIDENCE',
    title='[Actions Incident] PR production ledger: failure',
    reasons=('actions-incident',),
    action='evidence-not-a-gate',
)
