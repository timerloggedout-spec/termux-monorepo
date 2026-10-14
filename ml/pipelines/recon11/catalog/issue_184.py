"""Frozen recon11 observation. Not a merge decision. 2026-10-14."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=184,
    lane='NEED_EVIDENCE',
    title='credential inventory',
    reasons=('names-only',),
    action='probe-names-only',
    base='',
    login='',
    head_ref='',
)
