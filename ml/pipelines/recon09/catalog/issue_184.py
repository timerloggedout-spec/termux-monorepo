"""Frozen recon09 observation. Not a merge decision. Issue #175 / 2026-10-11."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=184,
    lane='CANDIDATE',
    title='Credential Authorizations & Last-Used Evidence',
    reasons=('names-only',),
    action='never-commit-secret-values',
    base='master',
    login='',
    head_ref='',
)
