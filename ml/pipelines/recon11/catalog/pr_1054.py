"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1054,
    lane='NEED_EVIDENCE',
    title='hindsight_wire: mount /v1 tool-calling + /v1/agent routers',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/hindsight-wire-invoke',
)
