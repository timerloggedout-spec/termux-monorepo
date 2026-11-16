"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1248,
    lane='EXTRACT',
    title='⚡ Bolt: CI Evaluators & Scout Performance Optimizations',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='bolt-ci-evaluators-performance-18246594067028114464',
)
