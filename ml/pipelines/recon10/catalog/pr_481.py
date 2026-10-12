"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=481,
    lane='EXTRACT',
    title='ops: make Jules PR handoffs observable',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='timerloggedout-spec',
    head_ref='ops/agent-handoff-observability',
)
