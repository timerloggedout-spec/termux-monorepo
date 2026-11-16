"""Frozen recon11 observation. Not a merge decision. Issue #175 / 2026-10-19."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='pr',
    number=1217,
    lane='EXTRACT',
    title='🛡️ Sentinel: Harden hub_mcp CLI and state directories against path traversal and symlink hijacking',
    reasons=('minesweeper-peer',),
    action='do-not-overwrite-peer',
    base='master',
    login='app/google-labs-jules',
    head_ref='sentinel/hub-mcp-path-symlink-hardening-2976150349998374501',
)
