"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=818,
    lane='NEED_EVIDENCE',
    title='feat(ops): Stepie MCP ops runbook + skill stamp + live goal bind',
    reasons=('dual-gate-unbound',),
    action='bind-dual-gate-on-this-sha',
    base='master',
    login='timerloggedout-spec',
    head_ref='feat/stepie-mcp-ops-20260924',
)
