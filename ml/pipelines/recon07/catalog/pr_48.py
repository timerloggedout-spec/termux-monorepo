"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=48,
    lane='EXTRACT',
    title='feat(llm-api-hub): OpenAI hub + standalone server + ADE/kai9000 split (TER-71)',
    reasons=('wrong-base:master-staging',),
    action='never-retarget-master',
    base='master-staging',
)
