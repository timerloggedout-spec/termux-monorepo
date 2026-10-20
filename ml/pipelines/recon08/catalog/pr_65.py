"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=65,
    lane='EXTRACT',
    title='🎨 Palette: Add pulsing heartbeat and color-blind accessible symbols to telemetry',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='jules-10011837884402998277-8685be83',
)
