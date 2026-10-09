"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=787,
    lane='EXTRACT',
    title='feat(ml): keep-alive DAG + ICM-CCTV re-extract on live tip (#175)',
    reasons=('ml-keep-alive-rebase-required',),
    action='extract-slice-only',
    base='master',
)
