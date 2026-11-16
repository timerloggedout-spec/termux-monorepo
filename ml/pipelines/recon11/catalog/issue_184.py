"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=184,
    lane='NEED_EVIDENCE',
    title='Credential Authorizations and Last-Used Evidence',
    reasons=('names-only', 'probed-2026-10-19'),
    action='names-only-no-secrets',
    base='',
    login='',
    head_ref='',
)
