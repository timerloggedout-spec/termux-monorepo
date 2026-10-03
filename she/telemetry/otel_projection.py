"""Project canonical agent events into an OpenTelemetry-shaped export.

The module intentionally has no OpenTelemetry dependency. The canonical JSONL
event remains the source of truth; installing an OTel SDK/exporter is optional.
"""

from __future__ import annotations

from datetime import datetime
from typing import Any, Mapping


EVENT_SPANS = {
    "agent.invoke": "invoke_agent",
    "agent.plan": "agent_plan",
    "workflow.invoke": "invoke_workflow",
    "tool.execute": "execute_tool",
    "mcp.session": "mcp_session",
    "mcp.operation": "mcp_operation",
    "a2a.delegate": "a2a_delegate",
    "a2a.result": "a2a_result",
    "evaluation.judgement": "evaluation_judgement",
    "provenance.snapshot": "provenance_snapshot",
    "environment.snapshot": "environment_snapshot",
    "artifact.produced": "artifact_produced",
}


def _epoch_nanos(value: str) -> int:
    stamp = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return int(stamp.timestamp() * 1_000_000_000)


def project_event(event: Mapping[str, Any]) -> dict[str, Any]:
    event_type = event["event_type"]
    span_name = EVENT_SPANS.get(event_type, event_type)
    attrs = dict(event.get("attributes") or {})
    attrs.update({
        "agent.id": event["agent_id"],
        "task.id": event["task_id"],
        "protocol": event.get("protocol", "other"),
        "event.status": event["status"],
    })
    if event.get("manager_id"):
        attrs["manager.id"] = event["manager_id"]
    if event.get("provider"):
        attrs["gen_ai.provider.name"] = event["provider"]
    if event.get("model"):
        attrs["gen_ai.request.model"] = event["model"]
    if event.get("tool_name"):
        attrs["gen_ai.tool.name"] = event["tool_name"]

    return {
        "trace_id": event["run_id"],
        "span_id": event["event_id"],
        "parent_span_id": event.get("parent_event_id"),
        "name": span_name,
        "start_time_unix_nano": _epoch_nanos(event["occurred_at"]),
        "attributes": attrs,
    }


def project_jsonl(events: list[Mapping[str, Any]]) -> list[dict[str, Any]]:
    return [project_event(event) for event in events]
