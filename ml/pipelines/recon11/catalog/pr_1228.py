"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1228,
    lane='EXTRACT',
    title='📖 Linguist: optimize CedrLang compress, caveman, and surface codec',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='linguist-cedrlang-opt-3085246636194873900',
)
