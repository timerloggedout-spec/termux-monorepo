"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=286,
    lane='NEED_EVIDENCE',
    title='feat(ops): evidence-gated autonomous staging progression',
    reasons=('wrong-base:master-staging',),
    action='never-retarget',
    base='master-staging',
    login='timerloggedout-spec',
    head_ref='feature/agentic-autonomy',
)
