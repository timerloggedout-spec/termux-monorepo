#!/usr/bin/env python3
"""Minimal Temporal Workflow + Activity smoke for termux-monorepo.

Self-host first: point at localhost:7233 (CLI start-dev or mcp-docker/temporal).
LangSmith plugin is optional — only activates when temporalio[langsmith] is
installed AND LANGSMITH_TRACING is truthy.

Not a dual-gate dependency. Capability-gated.
"""

from __future__ import annotations

import asyncio
import os
import sys
from datetime import timedelta


def _env(name: str, default: str) -> str:
    return os.environ.get(name, default).strip() or default


async def _run() -> int:
    try:
        from temporalio import activity, workflow
        from temporalio.client import Client
        from temporalio.worker import Worker
    except ImportError:
        print(
            "temporalio not installed. "
            "pip install 'temporalio'  # or: pip install 'temporalio[langsmith]'",
            file=sys.stderr,
        )
        return 2

    @activity.defn
    async def greet(name: str) -> str:
        return f"hello, {name}"

    @workflow.defn
    class HelloWorkflow:
        @workflow.run
        async def run(self, name: str) -> str:
            return await workflow.execute_activity(
                greet,
                name,
                schedule_to_close_timeout=timedelta(seconds=30),
            )

    address = _env("TEMPORAL_ADDRESS", "localhost:7233")
    namespace = _env("TEMPORAL_NAMESPACE", "default")
    task_queue = _env("TEMPORAL_TASK_QUEUE", "termux-agent")
    subject = _env("TEMPORAL_HELLO_NAME", "termux-monorepo")

    plugins = []
    tracing = _env("LANGSMITH_TRACING", "").lower() in {"1", "true", "yes"}
    if tracing:
        try:
            from temporalio.contrib.langsmith import LangSmithPlugin

            project = _env("LANGSMITH_PROJECT", "termux-monorepo-agents")
            plugins.append(LangSmithPlugin(project_name=project))
            print(f"LangSmithPlugin enabled project={project}")
        except ImportError:
            print(
                "LANGSMITH_TRACING set but temporalio[langsmith] not installed; "
                "continuing without plugin",
                file=sys.stderr,
            )

    client = await Client.connect(address, namespace=namespace, plugins=plugins)

    async with Worker(
        client,
        task_queue=task_queue,
        workflows=[HelloWorkflow],
        activities=[greet],
    ):
        result = await client.execute_workflow(
            HelloWorkflow.run,
            subject,
            id=f"hello-{subject}",
            task_queue=task_queue,
        )
        print(result)
    return 0


def main() -> None:
    raise SystemExit(asyncio.run(_run()))


if __name__ == "__main__":
    main()
