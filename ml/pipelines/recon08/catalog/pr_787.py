"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=787,
    lane='EXTRACT',
    title='feat(ml): keep-alive DAG + ICM-CCTV re-extract on live tip (#175)',
    reasons=('ml-wholesale-no-go',),
    action='extract-only-keep-pipelines',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/ml-keepalive-cctv-20260923-1314',
)
