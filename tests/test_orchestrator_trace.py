import json
from pathlib import Path

from she.observability.orchestrator_trace import JsonlTraceSink, OrchestratorTracer


def test_trace_is_hierarchical(tmp_path: Path):
    path = tmp_path / "trace.jsonl"
    tracer = OrchestratorTracer(JsonlTraceSink(path), benchmark_case_id="case-1")
    with tracer.span("orchestrator", role="orchestrator", deterministic=True, input_value={"value": 1}):
        with tracer.span("actor", role="actor", input_value={"value": 2}):
            pass
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    assert len(rows) == 2
    assert rows[0]["kind"] == "actor"
    assert rows[1]["kind"] == "orchestrator"
    assert rows[0]["parent_span_id"] == rows[1]["span_id"]
    assert rows[0]["trace_id"] == rows[1]["trace_id"]


def test_isolated_spawn_breaks_parent_context(tmp_path: Path):
    path = tmp_path / "trace.jsonl"
    tracer = OrchestratorTracer(JsonlTraceSink(path), benchmark_case_id="case-2")
    with tracer.span("orchestrator"):
        child = tracer.spawn(isolated=True)
        with child.span("spawn", spawn_mode="SPAWN", inherit_parent_context=False):
            pass
    row = json.loads(path.read_text().splitlines()[0])
    assert row["spawn_mode"] == "SPAWN"
    assert row["inherit_parent_context"] is False
