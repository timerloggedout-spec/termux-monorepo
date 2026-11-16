"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=48,
    lane='NEED_EVIDENCE',
    title='feat(llm-api-hub): OpenAI hub + standalone server + ADE/kai9000 split (TER-71)',
    reasons=('wrong-base:master-staging',),
    action='never-retarget',
    base='master-staging',
    login='timerloggedout-spec',
    head_ref='ter-41-hub-server-standalone',
)
