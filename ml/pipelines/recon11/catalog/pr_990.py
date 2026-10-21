"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=990,
    lane='NEED_EVIDENCE',
    title='feat(foresight): wire agent safety, orchestration, provenance, and gated edge lanes',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/foresight-agent-stack-2026-10-01',
)
