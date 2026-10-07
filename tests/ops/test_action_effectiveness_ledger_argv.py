"""Contract: ledger jq programs stay off argv so ARG_MAX cannot recur."""

from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORKFLOW = ROOT / ".github" / "workflows" / "action-effectiveness-ledger.yml"
CORRELATION = ROOT / "scripts" / "ci" / "ledger" / "correlation.jq"
STATE = ROOT / "scripts" / "ci" / "ledger" / "state.jq"


def test_ledger_filters_are_files_not_inline_argv():
    text = WORKFLOW.read_text(encoding="utf-8")
    assert CORRELATION.is_file()
    assert STATE.is_file()
    assert "scripts/ci/ledger/correlation.jq" in text
    assert "scripts/ci/ledger/state.jq" in text
    assert "state_json=" not in text
    assert "STATE_JSON" not in text
    assert '<<< "$correlation_json"' not in text
    # The failure class interpolated a jq program into the shell command.
    assert "correlation_json=\"$(jq" not in text
    assert "state_json=\"$(jq" not in text


def test_correlation_filter_emits_followthrough_shape():
    import json
    import shutil
    import subprocess

    if shutil.which("jq") is None:
        return
    comments = [{"id": 1, "body": "please fix the gate", "created_at": "2026-10-06T00:00:00Z"}]
    reviews = []
    inline = []
    commits = [{"sha": "abc", "commit": {"committer": {"date": "2026-10-06T01:00:00Z"}}}]
    proc = subprocess.run(
        [
            "jq",
            "-n",
            "--slurpfile",
            "comments",
            "/dev/stdin",
        ],
        input=json.dumps(comments),
        text=True,
        capture_output=True,
    )
    # jq cannot take four files from one stdin; write temps via python json and -f.
    import tempfile

    with tempfile.TemporaryDirectory() as tmp:
        base = Path(tmp)
        (base / "c.json").write_text(json.dumps(comments))
        (base / "r.json").write_text(json.dumps(reviews))
        (base / "i.json").write_text(json.dumps(inline))
        (base / "k.json").write_text(json.dumps(commits))
        out = subprocess.check_output(
            [
                "jq",
                "-n",
                "--slurpfile",
                "comments",
                str(base / "c.json"),
                "--slurpfile",
                "reviews",
                str(base / "r.json"),
                "--slurpfile",
                "inline",
                str(base / "i.json"),
                "--slurpfile",
                "commits",
                str(base / "k.json"),
                "-f",
                str(CORRELATION),
            ],
            text=True,
        )
    payload = json.loads(out)
    assert payload["all"][0]["relationship"] == "FOLLOWED_BY_COMMIT"
    assert payload["all"][0]["associated_commit_sha"] == "abc"
