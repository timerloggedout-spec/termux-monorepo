import os
import sys
import json
import urllib.request
import pytest
from unittest.mock import MagicMock

# Add scripts to path so we can import model_router
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
import scripts.model_router as mr

def test_parse_yaml(tmp_path):
    # Create a dummy yaml file
    yaml_content = """
# Test comment
version: 2
updated_at: "2026-08-09"
models:
  "model/a:free":
    elo: 1300
    role_suitability:
      review: 1.2
      triage: 0.8
  "model/b:free":
    elo: 1100
    role_suitability:
      review: 0.5
      triage: 1.5
"""
    yaml_file = tmp_path / "test_matrix.yaml"
    yaml_file.write_text(yaml_content)

    parsed = mr.parse_yaml(str(yaml_file))
    assert parsed["version"] == 2
    assert parsed["updated_at"] == "2026-08-09"
    assert parsed["models"]["model/a:free"]["elo"] == 1300
    assert parsed["models"]["model/a:free"]["role_suitability"]["review"] == 1.2
    assert parsed["models"]["model/b:free"]["elo"] == 1100
    assert parsed["models"]["model/b:free"]["role_suitability"]["triage"] == 1.5


def test_fetch_openrouter_free_models_success(monkeypatch):
    # Mock response from OpenRouter
    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "data": [
            {"id": "meta-llama/llama-3.3-70b-instruct:free", "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "google/gemma-3-12b-it:free", "pricing": {"prompt": "0", "completion": "0"}},
            {"id": "paid/model-example", "pricing": {"prompt": "0.0015", "completion": "0.002"}}
        ]
    }).encode("utf-8")

    # Configure the mock response as a proper context manager
    mock_response.__enter__.return_value = mock_response

    # Mock urllib.request.urlopen
    monkeypatch.setattr(urllib.request, "urlopen", lambda *args, **kwargs: mock_response)

    models = mr.fetch_openrouter_free_models()
    assert models is not None
    assert "meta-llama/llama-3.3-70b-instruct:free" in models
    assert "google/gemma-3-12b-it:free" in models
    assert "paid/model-example" not in models


def test_fetch_openrouter_free_models_failure(monkeypatch):
    # Simulate urllib network exception
    def mock_urlopen(*args, **kwargs):
        raise Exception("Network Timeout")

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    models = mr.fetch_openrouter_free_models()
    assert models is None


def test_fetch_openrouter_free_models_cached(tmp_path, monkeypatch):
    monkeypatch.setattr(mr, "COUNTER_DIR", str(tmp_path))

    mock_response = MagicMock()
    mock_response.read.return_value = json.dumps({
        "data": [
            {"id": "google/gemma-4-31b-it:free", "pricing": {"prompt": "0", "completion": "0"}}
        ]
    }).encode("utf-8")
    mock_response.__enter__.return_value = mock_response

    call_count = 0
    def mock_urlopen(*args, **kwargs):
        nonlocal call_count
        call_count += 1
        return mock_response

    monkeypatch.setattr(urllib.request, "urlopen", mock_urlopen)

    # First fetch should trigger network request
    models1 = mr.fetch_openrouter_free_models_cached()
    assert models1 == ["google/gemma-4-31b-it:free"]
    assert call_count == 1

    # Second fetch should use file cache and NOT trigger network request
    models2 = mr.fetch_openrouter_free_models_cached()
    assert models2 == ["google/gemma-4-31b-it:free"]
    assert call_count == 1


def test_usage_counters(tmp_path, monkeypatch):
    # Set COUNTER_DIR environment variable and reload mr.COUNTER_DIR
    monkeypatch.setenv("COUNTER_DIR", str(tmp_path))
    monkeypatch.setattr(mr, "COUNTER_DIR", str(tmp_path))

    # Usage should start at 0
    usage = mr.get_usage("openrouter", "google/gemma-3-12b-it:free")
    assert usage == 0

    # Increment usage
    new_usage = mr.increment_usage("openrouter", "google/gemma-3-12b-it:free")
    assert new_usage == 1

    # Read again
    usage = mr.get_usage("openrouter", "google/gemma-3-12b-it:free")
    assert usage == 1


def test_main_routing_decision_openrouter(tmp_path, monkeypatch, capsys):
    # Set up test environment
    monkeypatch.setenv("ROLE", "triage")
    monkeypatch.setenv("HAS_OMNI", "false")
    monkeypatch.setenv("HAS_OPENROUTER", "true")
    monkeypatch.setenv("HAS_GEMINI", "false")
    monkeypatch.setenv("COUNTER_DIR", str(tmp_path))
    monkeypatch.setattr(mr, "COUNTER_DIR", str(tmp_path))

    # Create mock success matrix
    matrix_content = """
models:
  "meta-llama/llama-3.3-70b-instruct:free":
    elo: 1300
    role_suitability:
      triage: 1.5
"""
    matrix_file = tmp_path / "model-success-matrix.yaml"
    matrix_file.write_text(matrix_content)

    # Redirect success matrix path cleanly without recursion
    original_parse_yaml = mr.parse_yaml
    monkeypatch.setattr(mr, "parse_yaml", lambda path: original_parse_yaml(str(matrix_file)) if "success" in path else {})

    # Mock polling to say meta-llama/llama-3.3-70b-instruct:free is available
    monkeypatch.setattr(mr, "fetch_openrouter_free_models_cached", lambda: ["meta-llama/llama-3.3-70b-instruct:free"])

    # Redirect GITHUB_OUTPUT
    go_file = tmp_path / "github_output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(go_file))

    # Run main
    mr.main()

    # Verify stdout outputs
    captured = capsys.readouterr()
    assert "::set-output name=provider::openrouter" in captured.out
    assert "::set-output name=model::meta-llama/llama-3.3-70b-instruct:free" in captured.out
    assert "::set-output name=skip::false" in captured.out

    # Verify GITHUB_OUTPUT file contents
    assert go_file.exists()
    outputs = go_file.read_text()
    assert "provider=openrouter" in outputs
    assert "model=meta-llama/llama-3.3-70b-instruct:free" in outputs
    assert "skip=false" in outputs


def test_main_routing_skips_unconfigured_models(tmp_path, monkeypatch, capsys):
    # Set up test environment
    monkeypatch.setenv("ROLE", "triage")
    monkeypatch.setenv("HAS_OMNI", "false")
    monkeypatch.setenv("HAS_OPENROUTER", "true")
    monkeypatch.setenv("HAS_GEMINI", "false")
    monkeypatch.setenv("COUNTER_DIR", str(tmp_path))
    monkeypatch.setattr(mr, "COUNTER_DIR", str(tmp_path))

    # Create mock success matrix scoring the unconfigured model highest
    matrix_content = """
models:
  "google/gemma-4-31b-it:free":
    elo: 2000
    role_suitability:
      triage: 2.0
  "meta-llama/llama-3.3-70b-instruct:free":
    elo: 1300
    role_suitability:
      triage: 1.0
"""
    matrix_file = tmp_path / "model-success-matrix.yaml"
    matrix_file.write_text(matrix_content)

    original_parse_yaml = mr.parse_yaml
    monkeypatch.setattr(mr, "parse_yaml", lambda path: original_parse_yaml(str(matrix_file)) if "success" in path else {})

    # Catalog reports both the unconfigured Gemma 4 model and the configured
    # Llama 3.3 model as available/free.
    monkeypatch.setattr(
        mr,
        "fetch_openrouter_free_models_cached",
        lambda: ["google/gemma-4-31b-it:free", "meta-llama/llama-3.3-70b-instruct:free"],
    )

    go_file = tmp_path / "github_output.txt"
    monkeypatch.setenv("GITHUB_OUTPUT", str(go_file))

    mr.main()

    captured = capsys.readouterr()
    assert "::set-output name=provider::openrouter" in captured.out
    assert "::set-output name=model::meta-llama/llama-3.3-70b-instruct:free" in captured.out
    assert "::set-output name=skip::false" in captured.out
    assert "gemma-4-31b-it" not in captured.out
    assert "gemma-4-26b-a4b-it" not in captured.out

    assert go_file.exists()
    outputs = go_file.read_text()
    assert "provider=openrouter" in outputs
    assert "model=meta-llama/llama-3.3-70b-instruct:free" in outputs
    assert "gemma-4" not in outputs
