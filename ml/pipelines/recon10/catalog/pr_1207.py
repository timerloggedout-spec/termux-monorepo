"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1207,
    lane='EXTRACT',
    title='📖 Linguist: Fast-Path Symbol Pre-Search and Module-Scope Expansion Tuples in CedrLang Protocol',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='linguist/cedrlang-symbol-presearch-opt-9405984631824400686',
)
