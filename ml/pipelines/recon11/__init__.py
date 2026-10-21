"""Observe-mode recon binder v0.11.0 for Issue #175.

Does not merge, force-push, restamp docs/ops/LANE-MATRIX.md, or pulse-comment.
Keeps frozen v0.8.0 (`recon`), v0.9.0 (`live`), v0.10.0 (`cut`), and the command-center DAG.
Master tip fd8c30ac is a docs index refresh, not a product promote.
"""
from ml.pipelines.recon11.roles import VERSION

__version__ = VERSION
