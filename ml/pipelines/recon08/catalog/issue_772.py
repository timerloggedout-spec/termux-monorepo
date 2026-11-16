"""Frozen recon observation. Not a merge decision. Issue #175 / 2026-10-10."""
from ml.pipelines.recon08.types import Observation

OBS = Observation(
    kind='issue',
    number=772,
    lane='SUPERSEDE',
    title='KNOWN: Actions / check surface stalls dual-gate-green PRs (Vercel rate-limit → mergeable_state unstable)',
    reasons=('vercel-non-gate',),
    action='ignore-vercel-rate-limit',
)
