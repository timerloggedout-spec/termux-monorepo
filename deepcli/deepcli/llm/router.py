"""Router — DeepSeek classifies a prompt into a layered plan, then dispatches."""
from __future__ import annotations
import json, re, sys
from pathlib import Path
from .base import Layer, Plan
from . import registry, quota

DEEPCLI = Path.home() / "deepcli"
sys.path.insert(0, str(DEEPCLI))

CLASSIFIER_PROMPT = """You are a routing classifier. Given a user request and a catalog of available apps, produce a LAYERED plan.

AVAILABLE APPS:
{catalog}

USER REQUEST:
{prompt}

KNOWN RECIPES (prefer these when the request matches):
- "scholarly research / papers / academic"     → [deepseek:refine-query] → [perplexity:orient] → [liner:deep-dive]
- "web research / current events"              → [deepseek:refine-query] → [perplexity:search]
- "summarize a document"                       → [deepseek]
- "coding task"                                → [deepseek] (fallback: blackbox)
- "long-form reading / book summary"           → [reedy] or [rdiscovery]
- "video note extraction"                      → [wisdomeye]
- "agent automation / multi-step web task"     → [manus] (fallback: genspark)
- "device automation"                          → [baozi]
- "email triage / search inbox"                → [gmail]

Return STRICT JSON, no prose:
{{
  "layers": [
    {{"role": "refine|research|orient|deep-dive|summarize|code|extract", "app": "app_name", "prompt": "specific prompt for this app"}}
  ],
  "rationale": "one sentence"
}}

RULES:
- 1-4 layers max.
- Prefer the recipe chain above when applicable.
- Use the most specialized app for each role.
- Non-LLM layers (research, orient, deep-dive, extract) produce text that FEEDS the next layer.
- Prompt for later layers can reference "INPUT FROM PREVIOUS LAYER" implicitly — the runtime will prepend it.
- Valid app names only from the catalog above.
- NEVER collapse a multi-step recipe into one layer if the recipe says 3 layers.
"""


def _classify(prompt: str) -> Plan:
    """Call DeepSeek directly to produce a Plan."""
    from deepcli.core import get_token, create_session, chat_completion
    tok = get_token()
    sid = create_session(tok, model_type="default")
    catalog = registry.catalog_for_classifier()
    full = CLASSIFIER_PROMPT.format(catalog=catalog, prompt=prompt)
    reply = chat_completion(tok, full, sid, max_continues=1)
    # extract JSON
    m = re.search(r"\{.*\}", reply, re.DOTALL)
    if not m:
        return Plan(layers=[Layer("route", "deepseek", prompt)],
                    rationale="classifier returned non-JSON; falling back to deepseek")
    try:
        parsed = json.loads(m.group(0))
    except Exception as e:
        return Plan(layers=[Layer("route", "deepseek", prompt)],
                    rationale=f"classifier JSON parse failed: {e}")
    layers = []
    for L in parsed.get("layers", []):
        # validate app name
        if registry.by_name(L.get("app", "")) is None:
            L["app"] = "deepseek"
        layers.append(Layer(role=L.get("role","route"),
                            app=L.get("app","deepseek"),
                            prompt=L.get("prompt", prompt)))
    return Plan(layers=layers, rationale=parsed.get("rationale",""))


def plan(prompt: str) -> Plan:
    """Public: classify without dispatching."""
    return _classify(prompt)


def dispatch(plan: Plan, execute: bool = False):
    """Walk the plan. If execute=False, return the plan with preview only."""
    results = []
    prev_output = ""
    for i, layer in enumerate(plan.layers):
        available, why = quota.is_available(layer.app)
        entry = {
            "index": i,
            "role": layer.role,
            "app": layer.app,
            "prompt": layer.prompt,
            "quota": {"available": available, "why": why},
        }
        if not execute:
            entry["status"] = "preview"
            results.append(entry)
            continue
        if not available:
            entry["status"] = "skipped-quota"
            results.append(entry)
            continue
        adapter = registry.resolve(layer.app)
        if adapter is None:
            entry["status"] = "no-adapter"
            results.append(entry)
            continue
        try:
            merged = layer.prompt
            if prev_output and layer.depends_on is None:
                merged = f"{layer.prompt}\n\nINPUT FROM PREVIOUS LAYER:\n{prev_output}"
            rep = adapter.ask(merged)
            quota.record_ok(layer.app)
            prev_output = rep.text
            entry["status"] = "ok"
            entry["reply_head"] = rep.text[:200]
            results.append(entry)
        except Exception as e:
            entry["status"] = f"error: {type(e).__name__}"
            entry["error"] = str(e)[:200]
            results.append(entry)
    return results


if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("prompt", nargs="+")
    ap.add_argument("--execute", action="store_true")
    ns = ap.parse_args()
    p = plan(" ".join(ns.prompt))
    print(f"rationale: {p.rationale}")
    for L in p.layers:
        print(f"  [{L.role:>10}] → {L.app:<14} {L.prompt[:70]}")
    print()
    res = dispatch(p, execute=ns.execute)
    print(json.dumps(res, indent=2))
