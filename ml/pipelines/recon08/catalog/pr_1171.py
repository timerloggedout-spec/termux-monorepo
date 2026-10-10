"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1171,
    lane='EXTRACT',
    title='📖 Linguist: optimize CedrLang line translation and surface codec callbacks',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='linguist-cedrlang-prefilter-optimization-8984121733734033572',
)
