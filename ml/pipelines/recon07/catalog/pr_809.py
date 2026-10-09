"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=809,
    lane='NEED_EVIDENCE',
    title='feat: move GAMUT remote and extend all-repo wiki knowledge fabric',
    reasons=('state:unknown',),
    action='rebase-small-slice',
    base='master',
)
