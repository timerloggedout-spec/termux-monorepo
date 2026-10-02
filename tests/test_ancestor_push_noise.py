"""Ancestor-push noise classification. No network."""

from __future__ import annotations

import importlib.util
from pathlib import Path


def _load():
    path = Path(__file__).resolve().parents[1] / "scripts" / "ci" / "ancestor_push_noise.py"
    spec = importlib.util.spec_from_file_location("ancestor_push_noise", path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_zero_job_ancestor_is_noise():
    mod = _load()
    assert mod.classify_ancestor_push("ahead", 0) == "ancestor_push_noise"


def test_identical_tip_is_current():
    mod = _load()
    assert mod.classify_ancestor_push("identical", 0) == "current"


def test_ancestor_with_jobs_is_current():
    mod = _load()
    assert mod.classify_ancestor_push("ahead", 2) == "current"


def test_diverged_is_current():
    mod = _load()
    assert mod.classify_ancestor_push("diverged", 0) == "current"
