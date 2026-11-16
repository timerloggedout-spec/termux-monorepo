"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1182,
    lane='EXTRACT',
    title='📖 Linguist: optimize CedrLang compression and expansion routines',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='perf/linguist-cedrlang-optimizations-7187129963119047466',
)
