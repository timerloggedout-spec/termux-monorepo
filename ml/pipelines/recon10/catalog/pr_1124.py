"""Frozen recon10 observation. Not a merge decision. Issue #175 / 2026-10-12."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1124,
    lane='EXTRACT',
    title='📖 Linguist: single-pass regex symbol alternation in CedrLang & Caveman protocol',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='linguist-cedrlang-symbol-optimization-16112434298601236484',
)
