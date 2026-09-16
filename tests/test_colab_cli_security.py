import os
import sys
import importlib.util
from pathlib import Path
import pytest
from click.testing import CliRunner

# Load colab-cli/bin/colab dynamically
colab_bin = Path(__file__).resolve().parent.parent / "colab-cli" / "bin" / "colab"
spec = importlib.util.spec_from_loader("colab_cli", importlib.machinery.SourceFileLoader("colab_cli", str(colab_bin)))
colab_cli = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(colab_cli)


def test_colab_cli_path_traversal_prevention():
    runner = CliRunner()

    # Test path traversal in start
    res_start = runner.invoke(colab_cli.cli, ["start", "--name", "../traversal"])
    assert res_start.exit_code != 0
    assert "Invalid sandbox name" in res_start.output

    # Test path traversal in stop
    res_stop = runner.invoke(colab_cli.cli, ["stop", "../traversal"])
    assert res_stop.exit_code != 0
    assert "Invalid sandbox name" in res_stop.output

    # Test path traversal in promote
    res_promote = runner.invoke(colab_cli.cli, ["promote", "../traversal"])
    assert res_promote.exit_code != 0
    assert "Invalid sandbox name" in res_promote.output


def test_colab_cli_promote_symlink_and_permissions(tmp_path, monkeypatch):
    runner = CliRunner()

    base_dir = tmp_path / "colab-cli"
    workspace_root = base_dir / "sandbox"
    production_root = base_dir / "production"
    workspace_root.mkdir(parents=True)
    production_root.mkdir(parents=True)

    # Mock BASE_DIR and config in colab_cli
    monkeypatch.setattr(colab_cli, "BASE_DIR", base_dir)
    test_config = {
        "colab": {
            "auth": {"cookie_file": "~/.config/colab/cookies.json"},
            "ssh": {"key_path": "~/.ssh/colab_rsa"},
            "default_runtime": "CPU",
            "workspace_root": str(workspace_root),
            "production_root": str(production_root)
        }
    }
    monkeypatch.setattr(colab_cli, "config", test_config)

    # Create dummy sandbox
    sandbox_path = workspace_root / "test-sandbox"
    sandbox_path.mkdir()
    (sandbox_path / "data.txt").write_text("sample data")

    # Test promotion
    res = runner.invoke(colab_cli.cli, ["promote", "test-sandbox", "--version", "v1"])
    assert res.exit_code == 0
    assert "Promoted to" in res.output

    # Verify latest symlink
    latest = production_root / "latest"
    assert latest.is_symlink()

    # Verify log file created with 0o600 and log_dir 0o700
    log_file = base_dir / "logs" / "promotions.log"
    assert log_file.exists()
    if os.name != "nt":
        assert (log_file.stat().st_mode & 0o777) == 0o600
        assert (log_file.parent.stat().st_mode & 0o777) == 0o700

    # Test symlink hijacking protection on promotions.log
    # Create symlink for log_file pointing to external target
    target_file = tmp_path / "sensitive.txt"
    target_file.write_text("sensitive")

    # Remove real log file and replace with symlink
    log_file.unlink()
    log_file.symlink_to(target_file)

    res_symlink = runner.invoke(colab_cli.cli, ["promote", "test-sandbox", "--version", "v2"])
    assert res_symlink.exit_code != 0
    assert "symlink hijacking" in res_symlink.output
    # Target file should not be modified
    assert target_file.read_text() == "sensitive"
