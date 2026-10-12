"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1204,
    lane='EXTRACT',
    title='⚡ Bolt: optimize live catalog feed evaluation and scoring',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='bolt/live-catalog-feed-perf-16852836025290040899',
)
