"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=432,
    lane='EXTRACT',
    title='feat(ml): observe-mode GitHub ML pipelines + Issue #175 matrix + PR minesweeper',
    reasons=('ml-wholesale-no-go',),
    action='extract-slice-only',
    base='master',
)
