"""Tests for ops/vm-backup: tiered export, scrub gate, state hash.

Synthetic HOME fixture; no network (publish is never invoked).
Phase 1 (scoping PR #3522): T0 content is staged; T1 is manifest-only.
"""
import json, os, subprocess, sys
from pathlib import Path

OPS = Path(__file__).resolve().parents[1] / "ops" / "vm-backup"
EXPORTER = OPS / "export_vm_workspace.py"
STATE_HASH = OPS / "state_hash.py"
FAKE_GHP = "ghp_" + "A" * 30


def _w(root: Path, rel: str, content: bytes = b"clean\n"):
    p = root / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(content)
    return p


def _git(args, cwd):
    subprocess.run(["git", "-C", str(cwd), "-c", "user.email=t@t",
                    "-c", "user.name=t"] + args, check=True,
                   capture_output=True)


def make_home(tmp: Path) -> Path:
    home = tmp / "home"
    home.mkdir()
    _w(home, "CLAUDE.md")
    _w(home, "MEMORY.md")
    _w(home, "memory/note.md")
    _w(home, "workspace/goals/g1/file.md")
    # a policy doc quoting the PEM pattern spec (ellipsis form, as in
    # the fleet's real SENSITIVITY-RULES doc): must NOT trip the gate
    policy = "detector: `-----BEGIN … PRIVATE " "KEY-----`\n"
    _w(home, "workspace/goals/g1/policy.md", policy.encode())
    _w(home, "workspace/custom-connectors/c1/CONNECTOR.md")
    # keys/ dir with a fake key: must never be staged. The header is
    # assembled in pieces so this fixture does not itself trip the
    # repo gate's no-secrets scan for key blocks.
    fake_key = ("-----BEGIN RSA PRIVATE " "KEY-----\nfake\n").encode()
    _w(home, "workspace/custom-connectors/c1/keys/app.pem", fake_key)
    _w(home, "workspace/user/u.txt")
    _w(home, "hooks/scripts/h.sh", b"#!/bin/sh\ntrue\n")
    _w(home, "workspace/scratch/junk.txt")
    # T1 loose file + plain dir + clone
    _w(home, "workspace/loose.txt")
    _w(home, "workspace/plain/file.txt")
    _w(home, "workspace/plain/node_modules/x.js", b"x")
    # secret-shaped plant in a NON-T0 location, denylisted by name:
    _w(home, "workspace/plain/.env", ("TOKEN=" + FAKE_GHP + "\n").encode())
    big = home / "workspace/plain/big.bin"
    with open(big, "wb") as f:
        f.truncate(26 * 1024 * 1024)  # sparse, over the 25 MB gate
    clone = home / "workspace/projclone"
    clone.mkdir(parents=True)
    _git(["init", "-q"], clone)
    _w(clone, "tracked.txt", b"v1\n")
    _git(["add", "."], clone)
    _git(["commit", "-qm", "init"], clone)
    _w(clone, "tracked.txt", b"v2 dirty\n")
    _w(clone, "untracked.txt")
    return home


def run_exporter(home: Path, staging: Path):
    return subprocess.run(
        [sys.executable, str(EXPORTER), "--home", str(home),
         "--staging", str(staging)],
        capture_output=True, text=True, timeout=300)


def manifest(staging: Path):
    return json.loads((staging / "MANIFEST.json").read_text())["files"]


def by_source(files):
    return {f["source"]: f for f in files}


def test_export_tiers_and_exclusions(tmp_path):
    home = make_home(tmp_path)
    staging = tmp_path / "stage"
    r = run_exporter(home, staging)
    assert r.returncode == 0, r.stdout + r.stderr
    # T0 content staged
    assert (staging / "t0/MEMORY.md").is_file()
    assert (staging / "t0/workspace/goals/g1/file.md").is_file()
    assert (staging / "t0/workspace/custom-connectors/c1/CONNECTOR.md").is_file()
    # keys/ content nowhere in staging
    assert not list(staging.rglob("app.pem"))
    assert not [p for p in staging.rglob("*") if "keys" in p.parts]
    files = by_source(manifest(staging))
    # T1 manifest-only shape assertions
    for src in ("workspace/loose.txt", "workspace/plain/file.txt",
                "workspace/projclone/tracked.txt",
                "workspace/projclone/untracked.txt"):
        e = files[src]
        assert e["tier"] == "t1" and e["exported"] is False
        assert e["reason"] == "phase1-manifest-only"
        assert e["path"] == "t1/" + src
        assert len(e["sha256"]) == 64 and e["size"] > 0
        assert not (staging / e["path"]).exists()  # no T1 content staged
    # big file: size rule noted distinctly
    big = files["workspace/plain/big.bin"]
    assert big["tier"] == "t1-manifest" and big["reason"] == "size"
    assert big["exported"] is False
    # denylisted plant excluded by name (no abort), keys plant excluded
    assert files["workspace/plain/.env"]["reason"] == "excluded:denylist-name"
    pem = files["workspace/custom-connectors/c1/keys/app.pem"]
    assert pem["exported"] is False
    assert pem["reason"].startswith("excluded:")
    # regenerable subtree never inventoried; scratch is a dir-level record
    assert not any("node_modules" in s for s in files)
    assert files["workspace/scratch"]["exported"] is False
    export_doc = json.loads((staging / "EXPORT.json").read_text())
    assert export_doc["gates"]["pass"] is True


def test_scrub_gate_aborts_on_secret_in_t0(tmp_path):
    home = make_home(tmp_path)
    _w(home, "memory/evil.md", ("leak " + FAKE_GHP + "\n").encode())
    staging = tmp_path / "stage"
    r = run_exporter(home, staging)
    assert r.returncode == 2
    export_doc = json.loads((staging / "EXPORT.json").read_text())
    assert export_doc["gates"]["pass"] is False
    assert export_doc["gates"]["content_scrub"] == "fail"
    # the planted path is named, the secret value is not echoed
    assert "memory/evil.md" in json.dumps(export_doc["gates"])
    assert FAKE_GHP not in json.dumps(export_doc)


def test_scrub_gate_aborts_on_real_key_header_in_t0(tmp_path):
    home = make_home(tmp_path)
    real_header = ("-----BEGIN RSA PRIVATE " "KEY-----\nfake\n").encode()
    _w(home, "memory/keydump.txt", real_header)
    staging = tmp_path / "stage"
    r = run_exporter(home, staging)
    assert r.returncode == 2
    export_doc = json.loads((staging / "EXPORT.json").read_text())
    assert export_doc["gates"]["content_scrub"] == "fail"


def test_state_hash_cycle(tmp_path):
    home = make_home(tmp_path)
    marker = tmp_path / "marker"

    def run(*extra):
        return subprocess.run(
            [sys.executable, str(STATE_HASH), "--home", str(home),
             "--marker", str(marker)] + list(extra),
            capture_output=True, text=True, timeout=120)

    assert run().returncode == 3          # no marker yet -> changed
    assert run("--write").returncode == 0
    assert run().returncode == 0          # unchanged
    mem = home / "MEMORY.md"
    mem.write_bytes(b"changed content\n")
    assert run().returncode == 3          # T0 changed -> export due


def test_split_band_stages_parts_and_restores(tmp_path):
    # Large-blob repair (2026-11-04): a T0 file in (SPLIT_AT, SIZE_GATE]
    # stages as byte-bounded parts + sidecar, never as one blob, and
    # restore reassembles it byte-exact.
    home = make_home(tmp_path)
    spend = home / "workspace/custom-connectors/c1/spend.jsonl"
    spend.parent.mkdir(parents=True, exist_ok=True)
    data = os.urandom(9 * 1024 * 1024)
    spend.write_bytes(data)
    staging = tmp_path / "stage"
    r = run_exporter(home, staging)
    assert r.returncode == 0, r.stdout + r.stderr
    files = by_source(manifest(staging))
    e = files["workspace/custom-connectors/c1/spend.jsonl"]
    assert e["exported"] is True
    assert len(e["split"]["parts"]) == 3
    assert e["split"]["part_size"] == 4 * 1024 * 1024
    assert e["split"]["total_size"] == len(data)
    assert (staging / "t0/workspace/custom-connectors/c1/spend.jsonl.split.json").is_file()
    for pr in e["split"]["parts"]:
        assert (staging / pr).stat().st_size <= 4 * 1024 * 1024
    export_doc = json.loads((staging / "EXPORT.json").read_text())
    assert export_doc["gates"]["pass"] is True
    assert export_doc["counts"]["split"] == 1
    restore = OPS / "restore_vm_workspace.py"
    target = tmp_path / "target"
    rr = subprocess.run(
        [sys.executable, str(restore), "--backup", str(staging),
         "--target", str(target), "--source-home", str(home)],
        capture_output=True, text=True, timeout=300)
    assert rr.returncode == 0, rr.stdout + rr.stderr
    drill = json.loads((target / "DRILL.json").read_text())
    assert drill["verdict"] == "pass"
    assert (target / "workspace/custom-connectors/c1/spend.jsonl").read_bytes() == data
