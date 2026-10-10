"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=724,
    lane='EXTRACT',
    title='feat(ml): slim keep-alive pipelines re-extract onto f1255c68 (#175)',
    reasons=('ml-wholesale-no-go',),
    action='extract-only-keep-pipelines',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/ml-pipelines-slim-20260921-1805',
)
