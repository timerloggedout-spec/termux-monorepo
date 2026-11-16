"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=184,
    lane='CANDIDATE',
    title='Credential Authorizations & Last-Used Evidence',
    reasons=('names-only',),
    action='record-names-never-values',
)
