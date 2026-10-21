"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1233,
    lane='EXTRACT',
    title='⚡ Bolt: optimize completion gate dispatch and lag index iso date parsing',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='bolt-perf-completion-gate-lag-index-3622676141182353567',
)
