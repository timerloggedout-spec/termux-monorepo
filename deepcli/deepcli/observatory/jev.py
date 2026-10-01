"""Jev — critic. LLM-as-judge against a rubric.

Role contract: (artifact_text, rubric, judge_provider, judge_model) ->
{scores: {field: value}, rationale, judge_provider, judge_model}
Rule: judge_provider/model MUST differ from artifact's producer.
"""
from __future__ import annotations
import json
from typing import Any


_RUBRIC_PROMPT = """You are an evaluator. Score the ARTIFACT against the
RUBRIC. Return strict JSON: {"scores": {<field>: <0-1>}, "rationale": "<one paragraph>"}.

RUBRIC:
{rubric}

ARTIFACT:
{artifact}
"""


async def critique(artifact: dict, rubric: dict,
                   judge_provider: str, judge_model: str,
                   client_factory=None) -> dict:
    if judge_provider == artifact.get("provider") and judge_model == artifact.get("model"):
        raise ValueError("Jev judge must differ from Mev producer (self-judging is degenerate)")

    if client_factory is None:
        from .mev import _default_client as client_factory

    client = client_factory(judge_provider, judge_model)
    prompt = _RUBRIC_PROMPT.format(
        rubric=json.dumps(rubric, indent=2),
        artifact=artifact.get("text", "")[:4000],
    )
    raw = await client.ask(prompt)
    text = getattr(raw, "text", str(raw))

    try:
        start = text.find("{")
        end = text.rfind("}")
        parsed = json.loads(text[start:end+1]) if start >= 0 and end > start else {}
    except Exception:
        parsed = {"scores": {}, "rationale": text[:400]}

    return {
        "role": "jev",
        "judge_provider": judge_provider,
        "judge_model": judge_model,
        "scores": parsed.get("scores", {}),
        "rationale": parsed.get("rationale", ""),
        "raw": text,
    }
