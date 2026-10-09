"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=682,
    lane='EXTRACT',
    title='feat(ml): keep-alive pipeline DAG + operator skills (Issue #175)',
    reasons=('ml-keep-alive-rebase-required',),
    action='extract-slice-only',
    base='master',
)
