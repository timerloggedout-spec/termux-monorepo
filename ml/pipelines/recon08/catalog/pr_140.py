"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=140,
    lane='EXTRACT',
    title='🎨 Palette: Stateful & Reactive PWA UX with Manual Vault Refresh & Accessibility',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='palette-pwa-reactive-ux-17363121820248065992',
)
