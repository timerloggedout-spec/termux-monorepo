"""Opt-in, fork-isolated adapter for immutable AdvancedResearch source pin.

The fork boundary is containment for this pinned runtime, not an OS sandbox.
"""
from __future__ import annotations

import hashlib
import json
import multiprocessing
import os
import tempfile
import threading
import time
from pathlib import Path
from queue import Empty
from typing import Any, Callable

PIN = "a262cb9d9703681c5a5066f03eb9fb89ad4d9cae"
MAX_QUERY, MAX_QUERIES, MAX_AGENTS, MAX_TOKENS, MAX_SECONDS, MAX_OUTPUT = 500, 3, 3, 2048, 60, 8000
SOURCE_HASHES = {
    "LICENSE": "187603d159fb72abba3b51626d70758b1fdcc7c8ecd3db99235aca8c28d6e6c6",
    "pyproject.toml": "f16bdf7d3b35e53c28518805e26652bc974ec490c0e191e5b81af9d1be10968f",
    "requirements.txt": "6859af53cb7d7f0169ceb1be9ef64ee73c7e57bcc89d202f8ba0de5fae194a75",
    "advanced_research/main.py": "80ffc55c595eddab36f211dea1896efa324f9d9fe3a094f0535cb71df840d9c3",
    "advanced_research/prompts.py": "5e73fe4d937204720eccd2f5c1e132fe25d7004b4bb880ada8832d0aff3e11ff",
}


def verify_source(root: Path) -> None:
    root = Path(root).resolve()
    for rel, digest in SOURCE_HASHES.items():
        path = (root / rel).resolve()
        if not path.is_relative_to(root) or not path.is_file():
            raise ValueError("pinned source verification failed")
        if hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError("pinned source verification failed")
    initializer = root / "advanced_research" / "__init__.py"
    if initializer.exists() and initializer.stat().st_size:
        raise ValueError("unexpected package initializer")


def validate(*, query: str, enabled: bool, agents: int, tokens: int,
             deadline_seconds: float, tools: tuple[str, ...]) -> None:
    if enabled is not True:
        raise PermissionError("AdvancedResearch execution is opt-in")
    if not isinstance(query, str) or not query.strip() or len(query) > MAX_QUERY:
        raise ValueError("query must contain 1..500 characters")
    if type(agents) is not int or not 1 <= agents <= MAX_AGENTS:
        raise ValueError("agent budget exceeds policy")
    if type(tokens) is not int or not agents + 1 <= tokens <= MAX_TOKENS:
        raise ValueError("token budget must cover director and each worker")
    if (isinstance(deadline_seconds, bool)
            or not isinstance(deadline_seconds, (int, float))
            or not 0 < deadline_seconds <= MAX_SECONDS):
        raise ValueError("deadline exceeds policy")
    if not tools or any(tool != "search" for tool in tools):
        raise ValueError("only injected search tool is permitted")


def _worker(root, workdir, query, agents, tokens, callbacks, correlation, ids, model, out):
    import sys
    import types
    import concurrent.futures

    os.chdir(workdir)
    verify_source(Path(root))
    search, inference = callbacks
    counts = {"search": 0, "inference": 0}
    count_lock = threading.Lock()
    per = tokens // (agents + 1)
    os.environ.clear()
    os.environ["PYTHONIOENCODING"] = "utf-8"
    stub_names = (
        "dotenv", "swarms", "swarms.prompts", "swarms.prompts.agent_conversation_aggregator",
        "swarms.structs", "swarms.structs.agent", "swarms.structs.conversation",
        "swarms.utils", "swarms.utils.history_output_formatter", "swarms_tools",
        "pydantic", "orjson", "loguru",
    )
    for name in stub_names:
        sys.modules[name] = types.ModuleType(name)
    sys.modules["dotenv"].load_dotenv = lambda *a, **k: False
    sys.modules["swarms.prompts.agent_conversation_aggregator"].AGGREGATOR_SYSTEM_PROMPT = ""

    class Conversation:
        def __init__(self, *a, **k):
            self.history = []

        def add(self, name, output):
            self.history.append((name, output))

        def get_history(self):
            return self.history

        def get_final_message(self):
            return self.history[-1][1] if self.history else ""

    sys.modules["swarms.structs.conversation"].Conversation = Conversation
    formatter = sys.modules["swarms.utils.history_output_formatter"]
    formatter.HistoryOutputType = list
    formatter.history_output_formatter = lambda conversation, type: conversation.get_final_message()
    sys.modules["pydantic"].BaseModel = type("BaseModel", (), {"__init__": lambda self, **kw: None})
    sys.modules["pydantic"].Field = lambda default=None, **kw: default
    sys.modules["orjson"].dumps = lambda *a, **k: b"{}"
    sys.modules["orjson"].OPT_INDENT_2 = 0
    sys.modules["loguru"].logger = types.SimpleNamespace(info=lambda *a, **k: None)

    def request_correlation(index: int) -> dict[str, str]:
        request_id = f"{correlation}-request-{index}"
        return {
            "run_id": ids[0] or correlation,
            "job_id": ids[1] or correlation,
            "request_id": request_id,
            "attempt_id": f"{request_id}-attempt-1",
            "parent_id": ids[2] or correlation,
            "adapter": "advanced-research",
            "source_revision": PIN,
        }

    class Agent:
        def __init__(self, **kwargs):
            self.kwargs = kwargs

        def run(self, task=None, img=None, **kwargs):
            toolset = self.kwargs.get("tools", [])
            if toolset and toolset[0] is not fake_search:
                return execute_tool(task)
            evidence = fake_search(task)
            with count_lock:
                counts["inference"] += 1
            agent_name = str(self.kwargs.get("agent_name", "worker-1"))
            index = int(agent_name.rsplit("-", 1)[-1]) + 1
            return inference(
                model,
                [{"role": "system", "content": str(self.kwargs.get("system_prompt", ""))[:1000]},
                 {"role": "user", "content": str(task)[:MAX_QUERY] + "\nEvidence:\n" + str(evidence)[:2000]}],
                per,
                correlation=request_correlation(index),
            )

    class PolicyError(ValueError):
        pass

    def execute_tool(raw):
        with count_lock:
            counts["inference"] += 1
        response = inference(
            model,
            [{"role": "system", "content": f"Director: return JSON with a queries array containing 1..{agents} bounded research queries."},
             {"role": "user", "content": str(raw)[:MAX_QUERY]}],
            per,
            correlation=request_correlation(0),
        )
        try:
            data = json.loads(response)
        except Exception:
            raise PolicyError("director response invalid") from None
        queries = data.get("queries") if isinstance(data, dict) else None
        if (not isinstance(queries, list) or not 1 <= len(queries) <= agents
                or any(not isinstance(item, str) or not item.strip() or len(item) > MAX_QUERY for item in queries)):
            raise PolicyError("director query policy violation")
        return upstream.execute_worker_search_agents(queries)

    sys.modules["swarms.structs.agent"].Agent = Agent

    def fake_search(text):
        with count_lock:
            counts["search"] += 1
            count = counts["search"]
        if count > agents or not isinstance(text, str) or len(text) > MAX_QUERY:
            raise PolicyError("search budget exceeded")
        result = search(text)
        return (result if isinstance(result, str) else str(result))[:2000]

    sys.modules["swarms_tools"].exa_search = fake_search
    real_executor = concurrent.futures.ThreadPoolExecutor
    concurrent.futures.ThreadPoolExecutor = lambda max_workers=None, **kw: real_executor(
        max_workers=min(agents, max_workers or agents), **kw
    )
    concurrent.futures.as_completed = lambda futures: iter(list(futures))
    try:
        package = types.ModuleType("advanced_research")
        package.__path__ = [str(Path(root) / "advanced_research")]
        sys.modules.pop("advanced_research", None)
        sys.modules.pop("advanced_research.main", None)
        sys.modules["advanced_research"] = package
        verify_source(Path(root))
        from advanced_research import main as upstream

        upstream.schema.worker_max_tokens = per
        runtime = upstream.AdvancedResearch(
            worker_model_name=model,
            director_model_name=model,
            director_max_tokens=per,
            max_loops=1,
            director_max_loops=1,
            export_on=False,
        )
        result = runtime.run(task=query)
        out.put({"ok": True, "result": str(result)[:MAX_OUTPUT], "calls": counts})
    except BaseException:
        out.put({"ok": False, "error": "pinned runtime failed"})


def execute(*, query: str, enabled: bool = False, agents: int = 1,
            tokens: int = 1024, deadline_seconds: float = 30,
            tools: tuple[str, ...] = ("search",), source_root: Path,
            inference: Callable[..., Any], search: Callable[..., Any],
            correlation_id: str, model: str | None = None,
            research_class: type | None = None,
            cancel: threading.Event | None = None, run_id: str | None = None,
            job_id: str | None = None, parent_id: str | None = None) -> dict[str, Any]:
    validate(query=query, enabled=enabled, agents=agents, tokens=tokens,
             deadline_seconds=deadline_seconds, tools=tools)
    if not callable(inference) or not callable(search):
        raise ValueError("inference and search callbacks must be callable")
    if not isinstance(model, str) or not model.strip():
        raise ValueError("an explicit model is required")
    if not isinstance(correlation_id, str) or not correlation_id or len(correlation_id) > 100:
        raise ValueError("valid correlation_id required")
    if research_class is not None:
        raise ValueError("custom research classes are forbidden")
    root = Path(source_root).resolve()
    verify_source(root)
    if cancel and cancel.is_set():
        raise InterruptedError("cancelled before execution")
    ctx = multiprocessing.get_context("fork")
    queue = ctx.Queue(maxsize=1)
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="advanced-research-") as workdir:
        process = ctx.Process(
            target=_worker,
            args=(str(root), workdir, query, agents, tokens, (search, inference),
                  correlation_id, (run_id, job_id, parent_id), model, queue),
            daemon=True,
        )
        try:
            process.start()
            deadline = started + deadline_seconds
            data = None
            while process.is_alive() and time.monotonic() < deadline:
                if cancel and cancel.is_set():
                    raise InterruptedError("cancelled")
                try:
                    data = queue.get(timeout=min(0.05, max(0, deadline - time.monotonic())))
                    break
                except Empty:
                    pass
            if data is None and process.is_alive():
                raise TimeoutError("research process exceeded deadline and was terminated")
            if data is None:
                try:
                    data = queue.get(timeout=0.2)
                except Exception:
                    raise RuntimeError("isolated pinned runtime failed") from None
            process.join(min(0.05, max(0, deadline - time.monotonic())))
            if not data.get("ok"):
                raise RuntimeError("isolated pinned runtime failed")
            return {"status": "completed", "correlation_id": correlation_id,
                    "source_revision": PIN, "result": data["result"],
                    "search_calls": data["calls"]["search"],
                    "inference_calls": data["calls"]["inference"],
                    "elapsed_seconds": round(time.monotonic() - started, 6)}
        finally:
            if process.is_alive():
                process.terminate()
                process.join(0.2)
                if process.is_alive():
                    process.kill()
                    process.join(0.5)
            queue.close()
            queue.join_thread()
