#!/usr/bin/env python3
"""Dynamic model router with AR-18 observe-mode capability decisions.

The provider/model execution route intentionally remains the existing Gemini-primary
path in this release. AR-18 only emits a bounded decision envelope so repository
outcomes can be measured before any active-routing policy changes.
"""

import json
import os
import re
import sys
import time

from scripts import capability_spine

COUNTER_DIR = os.environ.get("COUNTER_DIR", "/tmp/model-router")
KEY_VAL_RE = re.compile(r'^("[^"]+"|\'[^\']+\'|[^:]+):\s*(.*)$')

# Proven-only fallback when the OpenRouter catalog cannot be fetched. Newly listed
# free models remain ineligible until a live or stale catalog has observed them.
LEGACY_MODELS = {
    "meta-llama/llama-3.3-70b-instruct:free",
    "google/gemma-3-12b-it:free",
    "qwen/qwen3-coder:free",
    "deepseek/deepseek-r1:free",
    "auto/best-free",
}


def parse_yaml(filepath):
    if not os.path.exists(filepath):
        return {}
    result = {}
    path = []
    with open(filepath, "r", encoding="utf-8") as handle:
        for line in handle:
            stripped = line.strip()
            if not stripped or stripped.startswith("#"):
                continue
            indent = len(line) - len(line.lstrip())
            while path and path[-1][0] >= indent:
                path.pop()
            if not path:
                parent = result
                parent_key = None
            else:
                parent = path[-1][1]
                parent_key = path[-1][2]
            if stripped.startswith("- "):
                item_str = stripped[2:].strip()
                if ":" in item_str and not item_str.startswith(('"', "'")):
                    key, value = item_str.split(":", 1)
                    key = key.strip().strip('"\'')
                    value = value.strip().strip('"\'')
                    try:
                        value = float(value) if "." in value else int(value)
                    except ValueError:
                        pass
                    item_value = {key: value}
                else:
                    item_value = item_str.strip('"\'')
                    try:
                        item_value = float(item_value) if "." in item_value else int(item_value)
                    except ValueError:
                        pass
                if isinstance(parent, dict) and parent_key is not None:
                    if parent_key not in parent or not isinstance(parent[parent_key], list):
                        parent[parent_key] = []
                    parent[parent_key].append(item_value)
                    if isinstance(item_value, dict):
                        sub_key = next(iter(item_value))
                        path.append((indent, item_value, sub_key))
                continue
            match = KEY_VAL_RE.match(stripped)
            if not match:
                continue
            key = match.group(1).strip().strip('"\'')
            value = match.group(2).strip()
            if "#" in value:
                value = value.split("#")[0].strip()
            value = value.strip('"\'')
            if not value:
                new_dict = {}
                if isinstance(parent, dict):
                    parent[key] = new_dict
                path.append((indent, new_dict, key))
            else:
                if value.startswith("[") and value.endswith("]"):
                    parsed_value = [item.strip().strip('"\'') for item in value[1:-1].split(",")]
                elif value.lower() == "true":
                    parsed_value = True
                elif value.lower() == "false":
                    parsed_value = False
                else:
                    try:
                        parsed_value = float(value) if "." in value else int(value)
                    except ValueError:
                        parsed_value = value
                if isinstance(parent, dict):
                    parent[key] = parsed_value
                path.append((indent, parent, key))
    return result


def fetch_openrouter_free_models():
    """Poll OpenRouter's public catalog for currently free model IDs."""
    url = "https://openrouter.ai/api/v1/models"
    try:
        import urllib.request

        request = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(request, timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        free_models = []
        for model in data.get("data", []):
            model_id = model.get("id", "")
            pricing = model.get("pricing", {})
            try:
                free = model_id.endswith(":free") or (
                    float(pricing.get("prompt", 0.0)) == 0.0
                    and float(pricing.get("completion", 0.0)) == 0.0
                )
            except (ValueError, TypeError):
                free = model_id.endswith(":free")
            if free and model_id:
                free_models.append(model_id)
        return free_models or None
    except (OSError, ValueError, json.JSONDecodeError) as error:
        sys.stderr.write(
            f"Warning: Failed to poll OpenRouter models ({error}). Using hardcoded fallback list.\n"
        )
        return None


def fetch_openrouter_free_models_cached_with_source():
    """Return catalog models and one of live, cached, stale, or unavailable."""
    cache_file = os.path.join(COUNTER_DIR, "openrouter_models_cache.json")
    cached_models = None
    cached_time = 0
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r", encoding="utf-8") as handle:
                cache_data = json.load(handle)
            cached_models = cache_data.get("models")
            cached_time = cache_data.get("timestamp", 0)
        except (OSError, ValueError, TypeError, json.JSONDecodeError) as error:
            sys.stderr.write(f"Warning: OpenRouter cache is unreadable ({error}).\n")
    if cached_models is not None and time.time() - cached_time < 3600:
        sys.stderr.write("Using cached OpenRouter free models list.\n")
        return cached_models, "cached"
    models = fetch_openrouter_free_models()
    if models is not None:
        try:
            os.makedirs(COUNTER_DIR, exist_ok=True)
            with open(cache_file, "w", encoding="utf-8") as handle:
                json.dump({"timestamp": time.time(), "models": models}, handle)
        except (OSError, TypeError, ValueError) as error:
            sys.stderr.write(f"Warning: Could not persist OpenRouter catalog ({error}).\n")
        return models, "live"
    if cached_models is not None:
        sys.stderr.write("Warning: OpenRouter fresh poll failed. Falling back to stale cached models list.\n")
        return cached_models, "stale"
    return None, "unavailable"


def fetch_openrouter_free_models_cached():
    """Compatibility wrapper retained for callers and focused tests."""
    return fetch_openrouter_free_models_cached_with_source()[0]


def get_usage(provider, model):
    key = f"{provider}/{model}" if provider != "gemini" else model
    filename = os.path.join(COUNTER_DIR, key.replace("/", "_") + ".txt")
    if os.path.exists(filename):
        try:
            with open(filename, "r", encoding="utf-8") as handle:
                return int(handle.read().strip())
        except (OSError, ValueError) as error:
            sys.stderr.write(f"Warning: usage counter is unreadable ({error}).\n")
            return 0
    return 0


def increment_usage(provider, model):
    key = f"{provider}/{model}" if provider != "gemini" else model
    os.makedirs(COUNTER_DIR, exist_ok=True)
    filename = os.path.join(COUNTER_DIR, key.replace("/", "_") + ".txt")
    current = get_usage(provider, model)
    new_usage = current + 1
    with open(filename, "w", encoding="utf-8") as handle:
        handle.write(str(new_usage))
    return new_usage


def write_output(name, value):
    value = str(value)
    print(f"::set-output name={name}::{value}")
    output_path = os.environ.get("GITHUB_OUTPUT")
    if not output_path:
        return
    with open(output_path, "a", encoding="utf-8") as handle:
        if "\n" in value:
            handle.write(f"{name}<<AR18_EOF\n{value}\nAR18_EOF\n")
        else:
            handle.write(f"{name}={value}\n")


def emit_decision(
    role,
    success_matrix,
    limits,
    role_peers,
    role_residuals,
    has_omni,
    has_openrouter,
    has_gemini,
    openrouter_models,
    openrouter_catalog_state,
    target_sha=None,
    current_sha=None,
):
    """Emit AR-18 shadow data without affecting the legacy selected route."""
    if os.environ.get("CAPABILITY_SPINE_OBSERVE", "true").lower() != "true":
        write_output("decision", json.dumps({"schema_version": 2, "mode": "disabled"}))
        write_output("decision_summary", "capability-spine observe mode disabled")
        return

    catalog_models = openrouter_models
    catalog_state = openrouter_catalog_state
    if catalog_models is None:
        catalog_models = set(LEGACY_MODELS)
        catalog_state = "legacy"
    else:
        catalog_models = set(catalog_models)

    provider_flags = {
        "gemini": has_gemini,
        "omni": has_omni,
        "openrouter": has_openrouter,
    }
    pairs = [("gemini", model) for model in role_residuals.get(role, [])]
    pairs.extend(role_peers.get(role, []))
    candidates = []
    seen = set()
    for provider, model in pairs:
        key = (provider, model)
        if key in seen:
            continue
        seen.add(key)
        candidates.append(
            capability_spine.make_candidate(
                provider=provider,
                model=model,
                capability=role,
                declared_capabilities={role},
                effect="read_only_analysis",
                provenance={
                    "declared_source": "llm-peers.yaml/model-success-matrix.yaml",
                    "trusted": True,
                },
                policy_enabled=True,
                requires_current_sha=bool(target_sha),
                target_sha=target_sha,
                current_sha=current_sha,
                branch_write_confirmed=False,
                has_provider=provider_flags.get(provider, False),
                openrouter_models=catalog_models,
                openrouter_catalog_state=catalog_state,
                limits=limits,
                usage=get_usage(provider, model),
                success_entry=success_matrix.get("models", {}).get(model, {}),
            )
        )
    decision = capability_spine.compact_envelope(
        capability_spine.decide(capability=role, candidates=candidates)
    )
    write_output("decision", json.dumps(decision, separators=(",", ":"), sort_keys=True))
    write_output("decision_summary", decision["summary"])


def main():
    role = os.environ.get("ROLE", "triage")
    has_omni = os.environ.get("HAS_OMNI", "false").lower() == "true"
    has_openrouter = os.environ.get("HAS_OPENROUTER", "false").lower() == "true"
    has_gemini = os.environ.get("HAS_GEMINI", "true").lower() == "true"
    success_matrix = parse_yaml("docs/schemas/model-success-matrix.yaml")

    polled_free_models = None
    catalog_state = "unavailable"
    if has_openrouter:
        polled_free_models, catalog_state = fetch_openrouter_free_models_cached_with_source()

    limits = {
        "omni/auto/best-free": {"triage": 400, "review": 250, "invoke": 400},
        "openrouter/meta-llama/llama-3.3-70b-instruct:free": {"triage": 80, "review": 80, "invoke": 80},
        "openrouter/google/gemma-3-12b-it:free": {"triage": 80, "review": 80, "invoke": 80},
        "openrouter/qwen/qwen3-coder:free": {"triage": 60, "review": 60, "invoke": 60},
        "openrouter/deepseek/deepseek-r1:free": {"triage": 40, "review": 40, "invoke": 40},
        "openrouter/google/gemma-4-31b-it:free": {"triage": 80, "review": 80, "invoke": 80},
        "openrouter/google/gemma-4-26b-a4b-it:free": {"triage": 80, "review": 80, "invoke": 80},
        "openrouter/cohere/north-mini-code:free": {"triage": 60, "review": 60, "invoke": 60},
        "gemini-3.1-flash-lite": {"triage": 1400, "review": 1400, "invoke": 1400},
        "gemini-3.5-flash-lite": {"triage": 1400, "review": 1400, "invoke": 1400},
        "gemini-2.5-flash-lite": {"triage": 1000, "review": 1000, "invoke": 1000},
        "gemini-3.5-flash": {"triage": 1400, "review": 1400, "invoke": 1400},
        "gemini-2.5-flash": {"triage": 1400, "review": 1400, "invoke": 1400},
        "gemini-3-flash": {"triage": 1400, "review": 1400, "invoke": 1400},
    }
    role_peers = {
        "triage": [
            ("omni", "auto/best-free"),
            ("openrouter", "google/gemma-4-31b-it:free"),
            ("openrouter", "google/gemma-4-26b-a4b-it:free"),
            ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
            ("openrouter", "google/gemma-3-12b-it:free"),
        ],
        "review": [
            ("omni", "auto/best-free"),
            ("openrouter", "cohere/north-mini-code:free"),
            ("openrouter", "google/gemma-4-31b-it:free"),
            ("openrouter", "qwen/qwen3-coder:free"),
            ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
            ("openrouter", "deepseek/deepseek-r1:free"),
        ],
        "invoke": [
            ("omni", "auto/best-free"),
            ("openrouter", "google/gemma-4-31b-it:free"),
            ("openrouter", "google/gemma-4-26b-a4b-it:free"),
            ("openrouter", "meta-llama/llama-3.3-70b-instruct:free"),
            ("openrouter", "google/gemma-3-12b-it:free"),
        ],
    }
    role_residuals = {
        "triage": ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite", "gemini-2.5-flash-lite"],
        "review": ["gemini-3.5-flash", "gemini-2.5-flash", "gemini-3-flash", "gemini-3.1-flash-lite"],
        "invoke": ["gemini-3.1-flash-lite", "gemini-2.5-flash-lite"],
    }

    emit_decision(
        role,
        success_matrix,
        limits,
        role_peers,
        role_residuals,
        has_omni,
        has_openrouter,
        has_gemini,
        polled_free_models,
        catalog_state,
        target_sha=os.environ.get("TARGET_SHA") or None,
        current_sha=os.environ.get("CURRENT_SHA") or None,
    )

    # Existing execution selection stays unchanged in AR-18 observe mode.
    if has_gemini:
        gemini_candidates = []
        for model in role_residuals.get(role, []):
            model_entry = success_matrix.get("models", {}).get(model, {})
            score = model_entry.get("elo", 1000) * model_entry.get("role_suitability", {}).get(role, 1.0)
            gemini_candidates.append({"provider": "gemini", "model": model, "score": score})
        for candidate in sorted(gemini_candidates, key=lambda item: item["score"], reverse=True):
            model = candidate["model"]
            limit = limits.get(model, {}).get(role, 1000)
            used = get_usage("gemini", model)
            if used < limit:
                new_used = increment_usage("gemini", model)
                write_output("provider", "gemini")
                write_output("model", model)
                write_output("skip", "false")
                write_output(
                    "reason",
                    f"role={role} gemini={model} used={new_used}/{limit} (ranked score={candidate['score']}) PRIMARY",
                )
                return
            sys.stderr.write(f"Gemini primary soft budget exhausted: {model} ({used}/{limit})\n")

    peer_candidates = []
    for provider, model in role_peers.get(role, []):
        if provider == "omni" and not has_omni:
            continue
        if provider == "openrouter" and not has_openrouter:
            continue
        if provider == "openrouter" and not model.endswith(":free"):
            sys.stderr.write(f"Warning: non-free model ID '{model}' skipped.\n")
            continue
        if provider == "openrouter":
            permitted_models = polled_free_models if polled_free_models is not None else LEGACY_MODELS
            if model not in permitted_models:
                sys.stderr.write(f"Warning: OpenRouter model {model} is not in the permitted catalog. Skipping.\n")
                continue
        model_entry = success_matrix.get("models", {}).get(model, {})
        score = model_entry.get("elo", 1000) * model_entry.get("role_suitability", {}).get(role, 1.0)
        peer_candidates.append({"provider": provider, "model": model, "score": score})

    for candidate in sorted(peer_candidates, key=lambda item: item["score"], reverse=True):
        provider = candidate["provider"]
        model = candidate["model"]
        limit = limits.get(f"{provider}/{model}", {}).get(role, 40)
        used = get_usage(provider, model)
        if used < limit:
            new_used = increment_usage(provider, model)
            write_output("provider", provider)
            write_output("model", model)
            write_output("skip", "false")
            write_output(
                "reason",
                f"role={role} peer={provider} model={model} used={new_used}/{limit} (ranked score={candidate['score']}) secondary",
            )
            return
        sys.stderr.write(f"Peer soft budget exhausted: {provider}/{model} ({used}/{limit})\n")

    write_output("provider", "none")
    write_output("model", "")
    write_output("skip", "true")
    write_output("reason", f"all free paths exhausted (gemini primary + omni/openrouter secondary) role={role}")


if __name__ == "__main__":
    try:
        main()
    except (OSError, ValueError, KeyError, TypeError) as error:
        sys.stderr.write(f"Error: Model Router crashed: {error}\n")
        write_output("provider", "none")
        write_output("model", "")
        write_output("skip", "true")
        write_output("reason", f"Model Router crashed: {error}")
