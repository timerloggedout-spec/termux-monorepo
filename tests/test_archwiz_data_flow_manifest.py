import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[1]
BUILDER = ROOT / "archwiz" / "build_data_flow_manifest.py"
SCANNER = ROOT / "archwiz" / "trace_data_flow_safe.py"
LEGACY_SCANNER = ROOT / "archwiz" / "trace_data_flow.py"


def init_git_repo(path: Path) -> tuple[str, str]:
    path.mkdir(parents=True, exist_ok=True)
    subprocess.run(["git", "init", "-q", str(path)], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.name", "Test"], check=True)
    subprocess.run(["git", "-C", str(path), "config", "user.email", "test@example.invalid"], check=True)
    (path / "seed.txt").write_text("fixture\n")
    subprocess.run(["git", "-C", str(path), "add", "seed.txt"], check=True)
    subprocess.run(["git", "-C", str(path), "commit", "-qm", "seed"], check=True)
    sha = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD"], text=True).strip()
    tree = subprocess.check_output(["git", "-C", str(path), "rev-parse", "HEAD^{tree}"], text=True).strip()
    return sha, tree


def test_builder_cli_writes_explicit_output_with_provenance(tmp_path):
    repo = tmp_path / "repo root"
    sha, tree = init_git_repo(repo)
    index = tmp_path / "central index.jsonl"
    flow = tmp_path / "flow map.txt"
    output = tmp_path / "published output" / "DATA_FLOW_MANIFEST.md"
    index_bytes = (
        b'{"path":"project/data.json","size":120}\n'
        b'{"path":"other/data.json","size":20}\n'
    )
    flow_bytes = b"=== project/data.json ===\n  -> /home/example/project/writer.py\n"
    index.write_bytes(index_bytes)
    flow.write_bytes(flow_bytes)

    result = subprocess.run(
        [
            sys.executable, str(BUILDER), "--index", str(index), "--flow-map", str(flow),
            "--output", str(output), "--repo-root", str(repo),
        ],
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    manifest = output.read_text()
    assert f"**Source SHA:** {sha}" in manifest
    assert f"**Tree SHA:** {tree}" in manifest
    assert "**Generator version:**" in manifest
    assert f"**Input manifest SHA-256:** {hashlib.sha256(index_bytes).hexdigest()}" in manifest
    assert f"**Flow map SHA-256:** {hashlib.sha256(flow_bytes).hexdigest()}" in manifest
    assert "**Coverage status:** PARTIAL" in manifest
    assert "**Indexed files:** 2" in manifest
    assert "**Mapped files:** 1" in manifest
    assert "**Unmapped files:** 1" in manifest
    assert "candidate mention" in manifest.lower()
    assert "verified writer" not in manifest.lower()


def test_builder_missing_index_preserves_existing_output(tmp_path):
    output = tmp_path / "existing.md"
    output.write_text("previous snapshot\n")
    result = subprocess.run(
        [sys.executable, str(BUILDER), "--index", str(tmp_path / "missing.jsonl"),
         "--output", str(output), "--repo-root", str(tmp_path)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 2
    assert output.read_text() == "previous snapshot\n"
    assert "central index" in (result.stdout + result.stderr).lower()


def test_scanner_cli_honors_explicit_paths_and_safety_bounds(tmp_path):
    data_list = tmp_path / "data files.txt"
    source_root = tmp_path / "source root"
    output = tmp_path / "output map.txt"
    source_root.mkdir()
    (source_root / "writer.py").write_text('open("data/target.json", "w")\n')
    hidden = source_root / ".hidden"
    hidden.mkdir()
    (hidden / "hidden.py").write_text('"data/target.json"\n')
    cache = source_root / "node_modules"
    cache.mkdir()
    (cache / "cache.py").write_text('"data/target.json"\n')
    (source_root / "large.py").write_text('"data/target.json"\n' + ("x" * 200))
    linked_root = tmp_path / "linked"
    linked_root.mkdir()
    (linked_root / "linked.py").write_text('"data/target.json"\n')
    try:
        (source_root / "linked").symlink_to(linked_root, target_is_directory=True)
    except OSError:
        pass
    data_list.write_text("data/target.json\n")

    result = subprocess.run(
        [sys.executable, str(SCANNER), "--data-files", str(data_list),
         "--source-dir", str(source_root), "--output", str(output), "--max-file-bytes", "100"],
        capture_output=True, text=True, check=False,
    )

    assert result.returncode == 0, result.stdout + result.stderr
    mapping = output.read_text()
    assert "=== data/target.json ===" in mapping
    assert "writer.py" in mapping
    assert "hidden.py" not in mapping
    assert "cache.py" not in mapping
    assert "large.py" not in mapping
    assert "linked.py" not in mapping


def test_legacy_scanner_delegates_to_safe_cli(tmp_path):
    data_list = tmp_path / "data.txt"
    source_root = tmp_path / "src"
    output = tmp_path / "legacy output.txt"
    source_root.mkdir()
    (source_root / "reader.py").write_text('"data/item.json"\n')
    data_list.write_text("data/item.json\n")
    result = subprocess.run(
        [sys.executable, str(LEGACY_SCANNER), "--data-files", str(data_list),
         "--source-dir", str(source_root), "--output", str(output)],
        capture_output=True, text=True, check=False,
    )
    assert result.returncode == 0, result.stdout + result.stderr
    assert "reader.py" in output.read_text()
