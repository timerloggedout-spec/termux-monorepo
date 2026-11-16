from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

# Add scripts directory to path for import
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts" / "github"))

import historical_event_correlation as hec


def test_paged_hoisted_sep():
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps([{"id": 1}]).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    with patch("urllib.request.urlopen", return_value=mock_response):
        res, err = hec.paged("/repos/test/pulls?state=open", "token_xyz", pages=1)
        assert err is None
        assert len(res) == 1
        assert res[0]["id"] == 1


def test_collect_run_detail_uses_embedded_steps():
    jobs_response = [
        {
            "id": 101,
            "status": "completed",
            "conclusion": "success",
            "steps": [{"number": 1, "name": "Set up job", "status": "completed"}],
        }
    ]

    def mock_paged(path, token, pages):
        if "jobs" in path:
            return jobs_response, None
        if "artifacts" in path:
            return [], None
        return [], None

    with patch("historical_event_correlation.paged", side_effect=mock_paged):
        with patch("historical_event_correlation.get") as mock_get:
            run_id, jobs, artifacts, steps, errors = hec.collect_run_detail("owner/repo", "token", 1, 555)
            assert run_id == 555
            assert len(jobs) == 1
            assert steps == {101: [{"number": 1, "name": "Set up job", "status": "completed"}]}
            assert errors == []
            # Verify single-job API endpoint GET was skipped!
            mock_get.assert_not_called()


def test_collect_run_detail_fallback_when_steps_missing():
    jobs_response = [
        {
            "id": 102,
            "status": "completed",
            "conclusion": "success",
        }
    ]

    def mock_paged(path, token, pages):
        if "jobs" in path:
            return jobs_response, None
        if "artifacts" in path:
            return [], None
        return [], None

    with patch("historical_event_correlation.paged", side_effect=mock_paged):
        with patch("historical_event_correlation.get", return_value={"steps": [{"number": 1, "name": "Fallback Step"}]}) as mock_get:
            run_id, jobs, artifacts, steps, errors = hec.collect_run_detail("owner/repo", "token", 1, 556)
            assert run_id == 556
            assert steps == {102: [{"number": 1, "name": "Fallback Step"}]}
            assert errors == []
            mock_get.assert_called_once()
