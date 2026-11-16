"""Observe-mode recon binder v0.10.0 for Issue #175.

Does not merge, force-push, restamp docs/ops/LANE-MATRIX.md, or pulse-comment.
Keeps frozen v0.8.0 (`recon`) and frozen v0.9.0 (`live`) plus the command-center DAG.
Master tip df342068 is a help-wanted status refresh, not a product promote.
"""
from ml.pipelines.recon10.roles import VERSION

__version__ = VERSION
