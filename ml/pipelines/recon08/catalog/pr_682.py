"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=682,
    lane='EXTRACT',
    title='feat(ml): keep-alive pipeline DAG + operator skills (Issue #175)',
    reasons=('ml-wholesale-no-go',),
    action='extract-only-keep-pipelines',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/ml-pipeline-keep-20260920',
)
