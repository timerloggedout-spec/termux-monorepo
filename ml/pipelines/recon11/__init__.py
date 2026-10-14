"""Observe-mode recon binder v0.11.0 for Issue #175.

Records the 2026-10-14 names-only connector probe.
Does not merge, force-push, restamp docs/ops/LANE-MATRIX.md, or pulse-comment.
Does not replace frozen v0.8.0 (`recon`), v0.9.0 (`live`), or v0.10.0 (`cut`).
Master tip 3e64bc65 is a context backfill, not a product promote.
"""
from ml.pipelines.recon11.roles import VERSION

__version__ = VERSION
