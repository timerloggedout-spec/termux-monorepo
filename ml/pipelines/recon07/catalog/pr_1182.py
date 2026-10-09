"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-09."""
from ml.pipelines.recon07.types import Observation

OBS = Observation(
    kind='pr',
    number=1182,
    lane='EXTRACT',
    title='Linguist: optimize CedrLang compression and expansion routines',
    reasons=('bot-no-auto-promote', 'minesweeper-title',),
    action='do-not-overwrite-peer',
    base='master',
)
