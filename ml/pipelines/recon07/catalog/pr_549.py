"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=549,
    lane='EXTRACT',
    title='feat(ml): rebase observe-mode GitHub ML pipelines',
    reasons=('ml-wholesale-no-go',),
    action='extract-slice-only',
    base='master',
)
