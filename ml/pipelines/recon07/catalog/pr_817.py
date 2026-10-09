"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=817,
    lane='EXTRACT',
    title='feat(ml): keep-alive DAG re-extract onto 03ffb33b',
    reasons=('ml-keep-alive-rebase-required',),
    action='extract-slice-only',
    base='master',
)
