"""Optional, bounded Swarms SequentialWorkflow adapter (THUB-012)."""
from __future__ import annotations

import os
import sys
import tempfile
import threading
from contextlib import redirect_stdout
from typing import Any, Mapping

_ALLOWED = {"task", "model", "max_loops", "number_agents", "execute"}
_EXECUTION_LOCK = threading.Lock()


def validate_config(config: Mapping[str, Any]) -> dict[str, Any]:
    if not isinstance(config, Mapping):
        raise TypeError("config must be a mapping")
    unknown = set(config) - _ALLOWED
    if unknown:
        raise ValueError(f"unknown config keys: {', '.join(sorted(unknown))}")
    task = config.get("task")
    if not isinstance(task, str) or not task.strip():
        raise ValueError("task must be a nonblank string")
    model = config.get("model")
    if model is not None and (not isinstance(model, str) or not model.strip()):
        raise ValueError("model must be a nonblank string when supplied")
    loops = config.get("max_loops", 1)
    agents = config.get("number_agents", 2)
    for name, value, upper in (("max_loops", loops, 3), ("number_agents", agents, 2)):
        if type(value) is not int or not 1 <= value <= upper:
            raise ValueError(f"{name} must be an integer from 1 to {upper}")
    execute = config.get("execute", False)
    if type(execute) is not bool:
        raise TypeError("execute must be bool")
    if execute and model is None:
        raise ValueError("--execute requires an explicit model; no paid default is selected")
    return {"task": task.strip(), "model": model.strip() if model else None,
            "max_loops": loops, "number_agents": agents, "execute": execute}


class _HubLLM:
    """Minimal custom llm.run interface; sends requests only when Agent.run is called."""
    def __init__(self, model: str):
        self.model = model

    def run(self, task: str | None = None, **kwargs: Any) -> str:
        from llm_api_hub.clients.openai_compat import chat_completions, assistant_text
        # Pinned SDK passes task=None and messages=conversation by default.
        # Preserve role separation and the actual task rather than sending null.
        supplied = kwargs.get("messages")
        if supplied is not None:
            if not isinstance(supplied, list) or not supplied:
                raise ValueError("SDK messages must be a nonempty list")
            messages = []
            for message in supplied:
                if (not isinstance(message, dict)
                        or message.get("role") not in {"system", "user", "assistant"}
                        or not isinstance(message.get("content"), str)):
                    raise ValueError("SDK message must contain a supported role and text content")
                messages.append({"role": message["role"], "content": message["content"]})
        elif isinstance(task, str) and task.strip():
            messages = [{"role": "user", "content": task}]
        else:
            raise ValueError("SDK supplied neither text task nor conversation messages")
        response = chat_completions(messages, model=self.model)
        text = assistant_text(response)
        if not isinstance(text, str) or not text.strip():
            raise ValueError("Hub returned no assistant text")
        return text


def run(config: Mapping[str, Any], *, swarms_module: Any = None) -> dict[str, Any]:
    """Dry-run by default; create and run pinned Swarms workflow only on execute."""
    cfg = validate_config(config)
    result: dict[str, Any] = {
        "status": "dry_run" if not cfg["execute"] else "complete",
        "task": cfg["task"], "model": cfg["model"],
        "max_loops": cfg["max_loops"], "number_agents": cfg["number_agents"],
        "provider": "llm_api_hub OpenAI-compatible endpoint" if cfg["execute"] else None,
        "state_policy": "temporary external workspace, removed after execution",
    }
    if not cfg["execute"]:
        result["note"] = "Offline dry-run; pass execute=true and an explicit model to make model calls."
        return result
    # Upstream uses process-global environment/cwd and writes MEMORY.md even
    # with autosave=False. Serialize our runs and clean state on all exits.
    # This API is for the standalone CLI, not a concurrent embedded host.
    with _EXECUTION_LOCK, tempfile.TemporaryDirectory(prefix="termux-swarms-") as state, redirect_stdout(sys.stderr):
        previous = {key: os.environ.get(key) for key in ("WORKSPACE_DIR", "SWARMS_TELEMETRY_ON")}
        cwd = os.getcwd()
        try:
            os.environ["WORKSPACE_DIR"] = state
            os.environ["SWARMS_TELEMETRY_ON"] = "false"
            os.chdir(state)
            if swarms_module is None:
                from swarms import Agent, SequentialWorkflow
            else:
                Agent, SequentialWorkflow = swarms_module.Agent, swarms_module.SequentialWorkflow
            names = ["researcher", "reviewer"][:cfg["number_agents"]]
            agents = [Agent(agent_name=name, agent_description=f"{name} in a bounded sequential workflow",
                            system_prompt=f"You are the {name}. Complete only the provided task.",
                            llm=_HubLLM(cfg["model"]), model_name=cfg["model"], max_loops=1,
                            retry_attempts=1, tools=[], autosave=False, saved_state_path=None,
                            print_on=False, verbose=False, dynamic_loops=False)
                      for name in names]
            workflow = SequentialWorkflow(agents=agents, max_loops=cfg["max_loops"],
                                          autosave=False, verbose=False)
            # This caps workflow/agent loops, not total HTTP attempts.
            result["output"] = workflow.run(cfg["task"])
        finally:
            os.chdir(cwd)
            for key, value in previous.items():
                if value is None:
                    os.environ.pop(key, None)
                else:
                    os.environ[key] = value
    return result
