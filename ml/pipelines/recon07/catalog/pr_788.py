"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=788,
    lane='NEED_EVIDENCE',
    title='Linear TER-15 remainder',
    reasons=('wrong-base:master-staging',),
    action='never-retarget-master',
    base='master-staging',
)
