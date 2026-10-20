"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=746,
    lane='EXTRACT',
    title='feat(ml): slim keep-alive pipelines + ICM-CCTV on d10a7a54 (#175)',
    reasons=('ml-wholesale-no-go',),
    action='extract-only-keep-pipelines',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/ml-pipelines-slim-20260922-1218',
)
