"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=354,
    lane='NEED_EVIDENCE',
    title='fix(ops): bound all OX Alpha target context',
    reasons=('wrong-base:feat/ox-alpha-deepseek-canary-context-v2',),
    action='never-retarget',
    base='feat/ox-alpha-deepseek-canary-context-v2',
    login='timerloggedout-spec',
    head_ref='manus/ox-alpha-context-boundary',
)
