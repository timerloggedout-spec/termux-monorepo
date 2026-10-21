"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1218,
    lane='EXTRACT',
    title='🎨 Palette: improve ArchWiz cockpit responsiveness for Termux viewports',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='palette/archwiz-cockpit-ux-13908704319648797106',
)
