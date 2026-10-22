import importlib.util
import json
import signal
import threading
import time
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location(
    "advanced_research_adapter", ROOT / "src/advanced_research_adapter.py"
)
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)
SOURCE = ROOT / "integrations/swarms/advanced-research"


def args(**extra):
    defaults = dict(query="topic", enabled=True, agents=1, tokens=20,
                   deadline_seconds=3, tools=("search",))
    defaults.update(extra)
    return defaults


def test_policy_is_opt_in_integer_safe_and_tokens_cover_agents():
    with pytest.raises(PermissionError):
        mod.validate(**args(enabled=False))
    for changes in ({"agents": True}, {"tokens": True}, {"deadline_seconds": True},
                    {"agents": 4}, {"agents": 3, "tokens": 1}):
        with pytest.raises(ValueError):
            mod.validate(**args(**changes))


def test_source_lock_fails_closed(tmp_path):
    for rel in mod.SOURCE_HASHES:
        path = tmp_path / rel
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b"tampered")
    with pytest.raises(ValueError):
        mod.verify_source(tmp_path)


def test_nonempty_package_initializer_rejected(tmp_path):
    import shutil
    shutil.copytree(SOURCE, tmp_path, dirs_exist_ok=True)
    init = tmp_path / "advanced_research/__init__.py"
    init.write_text("raise RuntimeError('must never run')\n")
    with pytest.raises(ValueError):
        mod.verify_source(tmp_path)


def test_genuine_source_director_workers_use_stable_distinct_ids(tmp_path):
    trace = tmp_path / "trace.jsonl"
    marker = tmp_path / "cwd-marker"

    def mark(kind, value):
        with trace.open("a") as stream:
            stream.write(json.dumps([kind, value]) + "\n")

    def search(query):
        mark("search", query)
        return "evidence for " + query

    def inference(model, messages, max_tokens, *, correlation):
        text = " ".join(item.get("content", "") for item in messages)
        mark("infer", [model, text, max_tokens, correlation])
        if "initial question" in text:
            marker.write_text(str(Path.cwd()))
            return '{"queries":["generated topic A","generated topic B"]}'
        assert "evidence for generated topic" in text
        return "analysis using evidence"

    result = mod.execute(
        query="initial question", enabled=True, agents=2, tokens=64,
        deadline_seconds=10, source_root=SOURCE, inference=inference,
        search=search, correlation_id="corr-runtime", model="wrapper/deepseek",
        run_id="run", job_id="job", parent_id="parent",
    )
    rows = [json.loads(line) for line in trace.read_text().splitlines()]
    inference_rows = [value for kind, value in rows if kind == "infer"]
    ids = [row[3]["request_id"] for row in inference_rows]
    assert len(ids) == len(set(ids)) == 3
    assert ids.count("corr-runtime-request-0") == 1
    assert "corr-runtime-request-1" in ids and "corr-runtime-request-2" in ids
    assert all(row[0] == "wrapper/deepseek" for row in inference_rows)
    assert marker.exists() and Path(marker.read_text()) != Path.cwd()
    assert Path(marker.read_text()).is_relative_to(Path("/tmp"))
    assert result["search_calls"] == 2


def test_missing_model_rejected():
    with pytest.raises(ValueError, match="explicit model"):
        mod.execute(query="x", enabled=True, source_root=SOURCE,
                    inference=lambda *a, **k: "", search=lambda q: "",
                    correlation_id="missing-model")


def test_blocking_callback_ignoring_sigterm_is_killed_and_reaped():
    def block(*args, **kwargs):
        signal.signal(signal.SIGTERM, signal.SIG_IGN)
        while True:
            time.sleep(0.1)

    import multiprocessing
    before = {child.pid for child in multiprocessing.active_children()}
    start = time.monotonic()
    with pytest.raises(TimeoutError):
        mod.execute(query="x", enabled=True, agents=1, tokens=20,
                    deadline_seconds=0.25, source_root=SOURCE,
                    inference=block, search=lambda q: "e", correlation_id="timeout",
                    model="wrapper/deepseek")
    assert time.monotonic() - start < 2
    time.sleep(0.1)
    assert {child.pid for child in multiprocessing.active_children()} <= before


def test_cancel_kills_worker(tmp_path):
    event = threading.Event()
    marker = tmp_path / "started"
    result = []

    def infer(*args, **kwargs):
        marker.write_text("yes")
        time.sleep(3)
        return '{"queries":["x"]}'

    def call():
        try:
            mod.execute(query="x", enabled=True, agents=1, tokens=20,
                        deadline_seconds=8, source_root=SOURCE, inference=infer,
                        search=lambda q: "e", correlation_id="cancel",
                        model="wrapper/deepseek", cancel=event)
        except Exception as error:
            result.append(error)

    thread = threading.Thread(target=call)
    thread.start()
    for _ in range(40):
        if marker.exists():
            break
        time.sleep(0.05)
    assert marker.exists()
    event.set()
    thread.join(2)
    assert not thread.is_alive()
    assert result and isinstance(result[0], InterruptedError)


def test_import_has_no_execution_side_effects():
    assert mod.PIN and not hasattr(mod, "upstream")
