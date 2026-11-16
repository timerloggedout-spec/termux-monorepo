"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1151,
    lane='EXTRACT',
    title='🎨 Palette: UX and accessibility improvements for dashboard and Termux cockpit',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='palette-ux-a11y-improvements-2134469676251428008',
)
