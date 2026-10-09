"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=806,
    lane='NEED_EVIDENCE',
    title='ops: harden evaluation lanes and GitHub App capability evidence',
    reasons=('state:unknown',),
    action='rebase-small-slice',
    base='master',
)
