"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1186,
    lane='EXTRACT',
    title='⚡ Bolt: pre-compile regexes and fast-path set equality checks in CI evaluators',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='google-labs-jules[bot]',
    head_ref='jules-4403536697708655039-b50a480d',
)
