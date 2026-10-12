"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=601,
    lane='EXTRACT',
    title='feat(ml): extract observe-mode GitHub ML pipelines onto live master (#175)',
    reasons=('ml-wholesale-no-go',),
    action='extract-only-keep-pipelines',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/ml-pipelines-extract-c082f53',
)
