#!/usr/bin/env python3
"""
Model Router (Optimized Dynamic Adaptive-ness)
Implements Model Availability Polling with smart temporal caching,
dynamic ELO-based (3L0) ranking, and soft-budget validation.

Soft budgets raised 2026-08-10 (OPERATOR) to exceed prior free-tier headroom.
See .github/connectors/llm-peers.yaml for authorized catalog.

LEGACY_MODELS is the conservative catalog-unavailable allow-list: only models
proven in production. Newly listed free models must appear in a live/stale
OpenRouter poll before they are selected.

Verified and dynamic model routing logic.
"""

import os
import sys
import re
import json
import urllib.request
import time

COUNTER_DIR = os.environ.get("COUNTER_DIR", "/tmp/model-router")

# Proven-only fallback when OpenRouter catalog cannot be fetched.
# Do NOT add unverified free models here — they belong in role_peers and the live poll.
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
    with open(filepath, 'r', encoding='utf-8') as f:
        for line in f:
            stripped = line.strip()
            if not stripped or stripped.startswith('#'):
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
            if stripped.startswith('- '):
                item_str = stripped[2:].strip()
                if ':' in item_str and not (item_str.startswith('"') or item_str.startswith("'")):
                    k, v = item_str.split(':', 1)
                    k = k.strip().strip('"\'')
                    v = v.strip().strip('"\'')
                    try:
                        if '.' in v: v = float(v)
                        else: v = int(v)
                    except ValueError:
                        pass
                    item_val = {k: v}
                else:
                    item_val = item_str.strip('"\'')
                    try:
                        if '.' in item_val: item_val = float(item_val)
                        else: item_val = int(item_val)
                    except ValueError:
                        pass
                if isinstance(parent, dict) and parent_key is not None:
                    if parent_key not in parent or not isinstance(parent[parent_key], list):
                        parent[parent_key] = []
                    parent[parent_key].append(item_val)
                    if isinstance(item_val, dict):
                        sub_key = list(item_val.keys())[0]
                        path.append((indent, item_val, sub_key))
                continue
            m = re.match(r'^("[^"]+"|\'[^\']+\'|[^:]+):\s*(.*)$', stripped)
            if not m:
                continue
            key = m.group(1).strip().strip('"\'')
            val = m.group(2).strip()
            if '#' in val:
                val = val.split('#')[0].strip()
            val = val.strip('"\'')
            if not val:
                new_dict = {}
                if isinstance(parent, dict):
                    parent[key] = new_dict
                path.append((indent, new_dict, key))
            else:
                if val.startswith('[') and val.endswith(']'):
                    parsed_val = [v.strip().strip('"\'') for v in val[1:-1].split(',')]
                else:
                    if val.lower() == 'true':
                        parsed_val = True
                    elif val.lower() == 'false':
                        parsed_val = False
                    else:
                        try:
                            if '.' in val:
                                parsed_val = float(val)
                            else:
                                parsed_val = int(val)
                        except ValueError:
                            parsed_val = val
                if isinstance(parent, dict):
                    parent[key] = parsed_val
                path.append((indent, parent, key))
    return result

def fetch_openrouter_free_models():
    """Poll OpenRouter models endpoint; return free model ids or None on failure."""
    url = "https://openrouter.ai/api/v1/models"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as response:
            data = json.loads(response.read().decode('utf-8'))
            free_models = []
            for m in data.get('data', []):
                m_id = m.get('id', '')
                pricing = m.get('pricing', {})
                is_free = False
                if m_id.endswith(':free'):
                    is_free = True
                else:
                    try:
                        p_prompt = float(pricing.get('prompt', 0.0))
                        p_compl = float(pricing.get('completion', 0.0))
                        if p_prompt == 0.0 and p_compl == 0.0:
                            is_free = True
                    except (ValueError, TypeError):
                        pass
                if is_free and m_id:
                    free_models.append(m_id)
            if not free_models:
                return None
            return free_models
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to poll OpenRouter models ({e}). Using hardcoded fallback list.\n")
        return None

def fetch_openrouter_free_models_cached():
    """1h cache; on miss return stale cache if present, else live poll."""
    cache_file = os.path.join(COUNTER_DIR, "openrouter_models_cache.json")
    cached_models = None
    cached_time = 0
    if os.path.exists(cache_file):
        try:
            with open(cache_file, "r") as f:
                cache_data = json.load(f)
                cached_models = cache_data.get("models")
                cached_time = cache_data.get("timestamp", 0)
        except Exception:
            pass
    if cached_models is not None and (time.time() - cached_time < 3600):
        sys.stderr.write("Using cached OpenRouter free models list.\n")
        return cached_models
    models = fetch_openrouter_free_models()
    if models is not None:
        try:
            os.makedirs(COUNTER_DIR, exist_ok=True)
            with open(cache_file, "w") as f:
                json.dump({"timestamp": time.time(), "models": models}, f)
        except Exception:
            pass
        return models
    if cached_models is not None:
        sys.stderr.write("Warning: OpenRouter fresh poll failed. Falling back to stale cached models list.\n")
        return cached_models
    return None

def get_usage(provider, model):
    key = f"{provider}/{model}" if provider != "gemini" else model
    filename = os.path.join(COUNTER_DIR, key.replace('/', '_') + ".txt")
    if os.path.exists(filename):
        try:
            with open(filename, 'r') as f:
                return int(f.read().strip())
        except Exception:
            return 0
    return 0

def increment_usage(provider, model):
    key = f"{provider}/{model}" if provider != "gemini" else model
    os.makedirs(COUNTER_DIR, exist_ok=True)
    filename = os.path.join(COUNTER_DIR, key.replace('/', '_') + ".txt")
    current = get_usage(provider, model)
    with open(filename, 'w') as f:
        f.write(str(current + 1))
    return current + 1

def parse_soft_limits(val):
    if isinstance(val, dict):
        return val
    if isinstance(val, str):
        res = {}
        cleaned = val.replace("{", "").replace("}", "").strip()
        if cleaned:
            parts = cleaned.split(",")
            for part in parts:
                if ":" in part:
                    k, v = part.split(":", 1)
                    k = k.strip().strip("'\x22")
                    v = v.strip().strip("'\x22")
                    try:
                        res[k] = int(v)
                    except ValueError:
                        try:
                            res[k] = float(v)
                        except ValueError:
                            res[k] = v
        return res
    return {}

def main():
    role = os.environ.get("ROLE", "triage")
    has_omni = os.environ.get("HAS_OMNI", "false").lower() == "true"
    has_openrouter = os.environ.get("HAS_OPENROUTER", "false").lower() == "true"
    has_gemini = os.environ.get("HAS_GEMINI", "true").lower() == "true"

    matrix_path = "docs/schemas/model-success-matrix.yaml"
    success_matrix = parse_yaml(matrix_path)

    polled_free_models = None
    if has_openrouter:
        polled_free_models = fetch_openrouter_free_models_cached()

    # Dynamically load from llm-peers.yaml
    limits = {}
    role_peers = {"triage": [], "review": [], "invoke": []}
    role_residuals = {"triage": [], "review": [], "invoke": []}

    peers_data = parse_yaml(".github/connectors/llm-peers.yaml").get("peers", {})
    for provider, provider_data in peers_data.items():
        models_list = provider_data.get("models", {})
        if isinstance(models_list, dict):
            models_list = models_list.get("models", [])
        if not isinstance(models_list, list):
            models_list = []

        is_gemini = (provider == "gemini" or provider_data.get("residual_only") is True)

        for model_data in models_list:
            model_id = model_data.get("id")
            if not model_id:
                continue

            raw_limits = model_data.get("soft_limits", {})
            parsed_limits = parse_soft_limits(raw_limits)

            limit_key = model_id if is_gemini else f"{provider}/{model_id}"
            limits[limit_key] = parsed_limits

            if is_gemini:
                for r in ["triage", "review", "invoke"]:
                    if r in parsed_limits:
                        role_residuals[r].append(model_id)
            else:
                roles = model_data.get("roles", [])
                for r in roles:
                    if r in role_peers:
                        role_peers[r].append((provider, model_id))

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
            if polled_free_models is not None:
                if model not in polled_free_models:
                    sys.stderr.write(f"Warning: OpenRouter model {model} not in polled catalog. Skipping.\n")
                    continue
            else:
                if model not in LEGACY_MODELS:
                    sys.stderr.write(f"Warning: No catalog. Skipping unverified '{model}'.\n")
                    continue
        model_entry = success_matrix.get("models", {}).get(model, {})
        elo = model_entry.get("elo", 1000)
        suitability = model_entry.get("role_suitability", {}).get(role, 1.0)
        score = elo * suitability
        peer_candidates.append({"provider": provider, "model": model, "score": score})

    peer_candidates.sort(key=lambda x: x["score"], reverse=True)

    for candidate in peer_candidates:
        prov = candidate["provider"]
        mod = candidate["model"]
        limit_dict = limits.get(f"{prov}/{mod}", {})
        limit = limit_dict.get(role, limit_dict.get("default", 40))
        used = get_usage(prov, mod)
        if used < limit:
            new_used = increment_usage(prov, mod)
            reason = f"role={role} peer={prov} model={mod} used={new_used}/{limit} (ranked score={candidate['score']})"
            print(f"::set-output name=provider::{prov}")
            print(f"::set-output name=model::{mod}")
            print(f"::set-output name=skip::false")
            print(f"::set-output name=reason::{reason}")
            if "GITHUB_OUTPUT" in os.environ:
                with open(os.environ["GITHUB_OUTPUT"], "a") as go:
                    go.write(f"provider={prov}\nmodel={mod}\nskip=false\nreason={reason}\n")
            return
        sys.stderr.write(f"Peer soft budget exhausted: {prov}/{mod} ({used}/{limit})\n")

    if has_gemini:
        gemini_candidates = []
        for model in role_residuals.get(role, []):
            model_entry = success_matrix.get("models", {}).get(model, {})
            elo = model_entry.get("elo", 1000)
            suitability = model_entry.get("role_suitability", {}).get(role, 1.0)
            score = elo * suitability
            gemini_candidates.append({"provider": "gemini", "model": model, "score": score})
        gemini_candidates.sort(key=lambda x: x["score"], reverse=True)
        for candidate in gemini_candidates:
            mod = candidate["model"]
            limit_dict = limits.get(mod, {})
            limit = limit_dict.get(role, limit_dict.get("default", 15))
            used = get_usage("gemini", mod)
            if used < limit:
                new_used = increment_usage("gemini", mod)
                reason = f"role={role} gemini={mod} used={new_used}/{limit} (ranked score={candidate['score']}) residual"
                print(f"::set-output name=provider::gemini")
                print(f"::set-output name=model::{mod}")
                print(f"::set-output name=skip::false")
                print(f"::set-output name=reason::{reason}")
                if "GITHUB_OUTPUT" in os.environ:
                    with open(os.environ["GITHUB_OUTPUT"], "a") as go:
                        go.write(f"provider=gemini\nmodel={mod}\nskip=false\nreason={reason}\n")
                return
            sys.stderr.write(f"Gemini residual soft budget exhausted: {mod} ({used}/{limit})\n")

    reason = f"all free paths exhausted (omni/openrouter peers + gemini residual) role={role}"
    print("::set-output name=provider::none")
    print("::set-output name=model::")
    print("::set-output name=skip::true")
    print(f"::set-output name=reason::{reason}")
    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as go:
            go.write(f"provider=none\nmodel=\nskip=true\nreason={reason}\n")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        sys.stderr.write(f"Error: Model Router crashed: {e}\n")
        print("::set-output name=provider::none")
        print("::set-output name=model::")
        print("::set-output name=skip::true")
        print(f"::set-output name=reason::Model Router crashed: {e}")
        if "GITHUB_OUTPUT" in os.environ:
            try:
                with open(os.environ["GITHUB_OUTPUT"], "a") as go:
                    go.write(f"provider=none\nmodel=\nskip=true\nreason=Model Router crashed: {e}\n")
            except Exception:
                pass
