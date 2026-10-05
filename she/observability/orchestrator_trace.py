"""Privacy-preserving ATES runtime trace boundary."""
from __future__ import annotations
import contextvars, hashlib, json, secrets, time
from contextlib import contextmanager
from pathlib import Path
from datetime import datetime, timezone

_TRACE = contextvars.ContextVar("ates_trace_id", default=None)
_PARENT = contextvars.ContextVar("ates_parent_span_id", default=None)

def _new_id(): return secrets.token_hex(16)
def _now():
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
def fingerprint(value):
    raw = json.dumps(value, sort_keys=True, default=str, separators=(",", ":")).encode()
    return hashlib.sha256(raw).hexdigest()

class JsonlTraceSink:
    def __init__(self, path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
    def emit(self, record):
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(record, sort_keys=True, separators=(",", ":")) + "\n")

class OrchestratorTracer:
    def __init__(self, sink, benchmark_case_id):
        self.sink, self.benchmark_case_id = sink, benchmark_case_id
    @property
    def trace_id(self):
        value = _TRACE.get()
        if value is None:
            value = _new_id()
            _TRACE.set(value)
        return value
    @contextmanager
    def span(self, kind, **meta):
        parent = _PARENT.get()
        span_id = _new_id()
        token = _PARENT.set(span_id)
        started = time.perf_counter()
        state = {"status": "ok"}
        try:
            yield state
        except Exception as exc:
            state.update(status="error", error_type=type(exc).__name__)
            raise
        finally:
            state.pop("output", None)
            state.update(
                schema_version="ates.orchestrator.trace.v1",
                trace_id=self.trace_id,
                span_id=span_id,
                parent_span_id=parent,
                benchmark_case_id=self.benchmark_case_id,
                kind=kind,
                started_at=_now(),
                duration_ms=round((time.perf_counter() - started) * 1000, 3),
                **{k: v for k, v in meta.items() if k in {
                    "role", "spawn_mode", "inherit_parent_context",
                    "deterministic", "attributes"
                }}
            )
            if "context" in meta: state["context_fingerprint"] = fingerprint(meta["context"])
            if "input_value" in meta: state["input_fingerprint"] = fingerprint(meta["input_value"])
            self.sink.emit(state)
            _PARENT.reset(token)
    def spawn(self, isolated=True):
        child = OrchestratorTracer(self.sink, self.benchmark_case_id)
        if isolated:
            _TRACE.set(_new_id())
            _PARENT.set(None)
        return child
