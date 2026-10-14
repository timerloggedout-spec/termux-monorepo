"""Frozen recon11 observation. Not a merge decision. 2026-10-14."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=432,
    lane='EXTRACT',
    title='feat(ml): observe-mode GitHub ML pipelines + Issue #175 matrix',
    reasons=('ml-wholesale-no-go',),
    action='extract-only-keep-pipelines',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/ml-pipelines-init-175',
)
