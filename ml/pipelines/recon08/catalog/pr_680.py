"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=680,
    lane='EXTRACT',
    title='⚡ Bolt: optimize live_catalog_feed and add test coverage',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='bolt-live-catalog-feed-optimization-7117823810492674030',
)
