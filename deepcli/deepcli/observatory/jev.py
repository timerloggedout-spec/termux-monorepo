"""Jev - critic. LLM-as-judge against a rubric.

Role contract: (artifact_text, rubric, judge_provider, judge_model) ->
{scores: {field: value}, rationale, judge_provider, judge_model}
Rule: judge_provider/model MUST differ from artifact's producer.
"""

from __future__ import annotations

import json

_RUBRIC_PROMPT = """You are an evaluator. Score the ARTIFACT against the
RUBRIC. Return strict JSON: {"scores": {<field>: <0-1>}, "rationale": "<one paragraph>"}.

RUBRIC:
<<RUBRIC>>

ARTIFACT:
<<ARTIFACT>>
"""


def _render_prompt(rubric: dict, artifact_text: str) -> str:
    # str.format() cannot be used: the JSON rubric and the JSON example in
    # the template both contain literal braces. Replace sentinels instead.
    return _RUBRIC_PROMPT.replace("<<RUBRIC>>", json.dumps(rubric, indent=2)).replace(
        "<<ARTIFACT>>", artifact_text[:4000]
    )


def _parse_judgement(text: str) -> dict:
    # Best-effort extraction of the {scores, rationale} object from the raw
    # judge reply. When the reply carries no JSON object at all (or is not
    # valid JSON), fall back to the raw text as the rationale so the caller
    # never silently loses the judge's reasoning.
    start = text.find("{")
    end = text.rfind("}")
    if start >= 0 and end > start:
        try:
            return json.loads(text[start : end + 1])
        except Exception:
            pass
    return {"scores": {}, "rationale": text[:400]}


async def critique(
    artifact: dict,
    rubric: dict,
    judge_provider: str,
    judge_model: str,
    client_factory=None,
) -> dict:
    if judge_provider == artifact.get("provider") and judge_model == artifact.get(
        "model"
    ):
        raise ValueError(
            "Jev judge must differ from Mev producer (self-judging is degenerate)"
        )

    if client_factory is None:
        from .mev import _default_client as client_factory

    client = client_factory(judge_provider, judge_model)
    prompt = _render_prompt(rubric, artifact.get("text", ""))
    raw = await client.ask(prompt)
    text = getattr(raw, "text", str(raw))

    parsed = _parse_judgement(text)

    return {
        "role": "jev",
        "judge_provider": judge_provider,
        "judge_model": judge_model,
        "scores": parsed.get("scores", {}),
        "rationale": parsed.get("rationale", ""),
        "raw": text,
    }
