"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=103,
    lane='NEED_EVIDENCE',
    title='feat(comms): CAVEMAN-micro seed + success matrix',
    reasons=('state:unknown',),
    action='hold-for-evidence',
    base='master',
)
