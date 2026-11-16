"""System One stage — verify a text with a decision model.

Maps an observatory rubric onto System One questions: each rubric
field becomes a Score question whose criteria are the two endpoints
["0", "1"], so the server's interpolated score IS the 0..1 field
score; plus a Noul question asking whether the text is free of
fabricated claims. Returns the observatory's in-band result shape
({role, ok, scores, ...}); transport failures come back ok: False
with the error, never raised, so a dispatch records them like any
other stage failure.

The endpoint is any TypeSafe-compatible server (see
llm/adapters/systemone.py): a self-hosted Kev / simple-jev / Ollaya,
or a public demo. No credential is required for local servers.
"""
from __future__ import annotations

DEFAULT_RUBRIC = {
    "quality": "0..1 overall quality of the response",
    "grounding": "0..1 factual grounding; penalize fabrication",
}

SUPPORTED_INSTRUCTIONS = (
    "Is the text free of fabricated claims — every claim supported "
    "rather than invented?")


def rubric_questions(rubric: dict) -> dict:
    questions = {
        field: {"type": "score", "instructions": str(desc),
                "criteria": ["0", "1"]}
        for field, desc in rubric.items()
    }
    questions["supported"] = {
        "type": "noul", "instructions": SUPPORTED_INSTRUCTIONS}
    return questions


async def decide_check(state: str, rubric: dict | None = None,
                       base_url: str = "", model: str = "",
                       transport=None) -> dict:
    rubric = rubric or DEFAULT_RUBRIC
    from ..llm.adapters.systemone import Adapter

    client = Adapter(transport=transport,
                     base_url=base_url or None)
    if model:
        client.model = model
    try:
        dec = await client.decide(state, rubric_questions(rubric))
    except Exception as e:  # stage failures are recorded, not raised
        return {"role": "systemone", "ok": False,
                "model": model or client.model,
                "base_url": client.base_url,
                "error": f"{type(e).__name__}: {e}"}
    scores = {}
    for field in rubric:
        ans = dec.answers.get(field, {})
        if isinstance(ans, dict) and "score" in ans:
            scores[field] = ans["score"]
    supported = dec.answers.get("supported", {})
    return {
        "role": "systemone",
        "ok": bool(dec.answers),
        "model": dec.model,
        "base_url": client.base_url,
        "scores": scores,
        "supported": supported.get("noul") if isinstance(
            supported, dict) else None,
        "answers": dec.answers,
        "tokens_in": dec.tokens_in,
        "tokens_out": dec.tokens_out,
        "latency_ms": dec.latency_ms,
    }
