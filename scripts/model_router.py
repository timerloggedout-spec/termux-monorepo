#!/usr/bin/env python3
"""
Model Router (Optimized Dynamic Adaptive-ness)
Implements Model Availability Polling, dynamic ELO-based (3L0) ranking,
and soft-budget budget validation for triage, review, and invoke roles.

This script replaces rigid bash logic with robust Python standard library code.
"""

import os
import sys
import re
import json
import urllib.request
import ssl

COUNTER_DIR = os.environ.get("COUNTER_DIR", "/tmp/model-router")

def parse_yaml(filepath):
    """
    Minimal robust YAML parser for standard key-value and indentation structures.
    Does not require external dependencies like PyYAML.
    """
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
    """
    Polls the OpenRouter models endpoint to find available free models.
    """
    url = "https://openrouter.ai/api/v1/models"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        # Use standard SSL verification by default for secure transfers
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
                    # Robust check converting pricing prompt/completion to float
                    try:
                        p_prompt = float(pricing.get('prompt', 0.0))
                        p_compl = float(pricing.get('completion', 0.0))
                        if p_prompt == 0.0 and p_compl == 0.0:
                            is_free = True
                    except (ValueError, TypeError):
                        pass

                if is_free and m_id:
                    free_models.append(m_id)
            return free_models
    except Exception as e:
        sys.stderr.write(f"Warning: Failed to poll OpenRouter models ({e}). Using hardcoded fallback list.\n")
        return None


def get_usage(provider, model):
    """
    Returns the daily counter for a model.
    """
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
    """
    Increments and saves the daily counter for a model.
    """
    key = f"{provider}/{model}" if provider != "gemini" else model
    os.makedirs(COUNTER_DIR, exist_ok=True)
    filename = os.path.join(COUNTER_DIR, key.replace('/', '_') + ".txt")
    current = get_usage(provider, model)
    with open(filename, 'w') as f:
        f.write(str(current + 1))
    return current + 1


def main():
    # Load input arguments or environment variables
    role = os.environ.get("ROLE", "triage")
    has_omni = os.environ.get("HAS_OMNI", "false").lower() == "true"
    has_openrouter = os.environ.get("HAS_OPENROUTER", "false").lower() == "true"
    has_gemini = os.environ.get("HAS_GEMINI", "true").lower() == "true"

    # Load configuration schemas
    matrix_path = "docs/schemas/model-success-matrix.yaml"
    success_matrix = parse_yaml(matrix_path)

    # 1. Poll OpenRouter models for availability
    polled_free_models = fetch_openrouter_free_models()

    # 2. Define candidates per role and retrieve limit mapping
    # Defaults in case schemas are missing or incomplete
    limits = {
        "omni/auto/best-free": {"triage": 200, "review": 120, "invoke": 200},
        "openrouter/meta-llama/llama-3.3-70b-instruct:free": {"triage": 40, "review": 40, "invoke": 40},
        "openrouter/google/gemma-3-12b-it:free": {"triage": 40, "review": 40, "invoke": 40},
        "openrouter/qwen/qwen3-coder:free": {"triage": 30, "review": 30, "invoke": 30},
        "openrouter/deepseek/deepseek-r1:free": {"triage": 20, "review": 20, "invoke": 20},
        "openrouter/google/gemma-4-31b-it:free": {"triage": 40, "review": 40, "invoke": 40},
        "openrouter/google/gemma-4-26b-a4b-it:free": {"triage": 40, "review": 40, "invoke": 40},
        "openrouter/cohere/north-mini-code:free": {"triage": 30, "review": 30, "invoke": 30},
        "gemini-3.1-flash-lite": {"triage": 450, "review": 450, "invoke": 450},
        "gemini-3.5-flash-lite": {"triage": 450, "review": 450, "invoke": 450},
        "gemini-2.5-flash-lite": {"triage": 15, "review": 15, "invoke": 15},
        "gemini-3.5-flash": {"triage": 15, "review": 15, "invoke": 15},
        "gemini-2.5-flash": {"triage": 15, "review": 15, "invoke": 15},
        "gemini-3-flash": {"triage": 15, "review": 15, "invoke": 15},
    }

    # Preferred lists per role
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
        "invoke": ["gemini-3.1-flash-lite", "gemini-3.5-flash-lite"],
    }

    # 3. Score and rank peer candidates
    peer_candidates = []
    for provider, model in role_peers.get(role, []):
        if provider == "omni" and not has_omni:
            continue
        if provider == "openrouter" and not has_openrouter:
            continue
        if provider == "openrouter" and not model.endswith(":free"):
            sys.stderr.write(f"Warning: Skipping non-:free OpenRouter model {model}.\n")
            continue

        # Cross-reference OpenRouter polled availability
        if provider == "openrouter" and polled_free_models is not None:
            if model not in polled_free_models:
                sys.stderr.write(f"Warning: OpenRouter model {model} is not currently available/free in polled catalog. Skipping.\n")
                continue

        # Calculate ELO score from success matrix (ELO ≈ 3L0)
        model_entry = success_matrix.get("models", {}).get(model, {})
        elo = model_entry.get("elo", 1000)
        suitability = model_entry.get("role_suitability", {}).get(role, 1.0)
        score = elo * suitability

        peer_candidates.append({
            "provider": provider,
            "model": model,
            "score": score
        })

    # Sort peers by ELO score descending
    peer_candidates.sort(key=lambda x: x["score"], reverse=True)

    # 4. Attempt routing to highest ranked peer with capacity
    for candidate in peer_candidates:
        prov = candidate["provider"]
        mod = candidate["model"]
        limit_dict = limits.get(f"{prov}/{mod}", {})
        limit = limit_dict.get(role, limit_dict.get("default", 40))

        used = get_usage(prov, mod)
        if used < limit:
            new_used = increment_usage(prov, mod)
            print(f"::set-output name=provider::{prov}")
            print(f"::set-output name=model::{mod}")
            print(f"::set-output name=skip::false")
            print(f"::set-output name=reason::role={role} peer={prov} model={mod} used={new_used}/{limit} (ranked score={candidate['score']})")

            # GITHUB_OUTPUT file support (newer GitHub Actions convention)
            if "GITHUB_OUTPUT" in os.environ:
                with open(os.environ["GITHUB_OUTPUT"], "a") as go:
                    go.write(f"provider={prov}\n")
                    go.write(f"model={mod}\n")
                    go.write(f"skip=false\n")
                    go.write(f"reason=role={role} peer={prov} model={mod} used={new_used}/{limit} (ranked score={candidate['score']})\n")
            return

        sys.stderr.write(f"Peer soft budget exhausted: {prov}/{mod} ({used}/{limit})\n")

    # 5. Fallback to Gemini residuals if peers are exhausted
    if has_gemini:
        gemini_candidates = []
        for model in role_residuals.get(role, []):
            model_entry = success_matrix.get("models", {}).get(model, {})
            elo = model_entry.get("elo", 1000)
            suitability = model_entry.get("role_suitability", {}).get(role, 1.0)
            score = elo * suitability

            gemini_candidates.append({
                "provider": "gemini",
                "model": model,
                "score": score
            })

        # Sort Gemini candidates by ELO score descending
        gemini_candidates.sort(key=lambda x: x["score"], reverse=True)

        for candidate in gemini_candidates:
            mod = candidate["model"]
            limit_dict = limits.get(mod, {})
            limit = limit_dict.get(role, limit_dict.get("default", 15))

            used = get_usage("gemini", mod)
            if used < limit:
                new_used = increment_usage("gemini", mod)
                print(f"::set-output name=provider::gemini")
                print(f"::set-output name=model::{mod}")
                print(f"::set-output name=skip::false")
                print(f"::set-output name=reason::role={role} gemini={mod} used={new_used}/{limit} (ranked score={candidate['score']}) residual")

                if "GITHUB_OUTPUT" in os.environ:
                    with open(os.environ["GITHUB_OUTPUT"], "a") as go:
                        go.write(f"provider=gemini\n")
                        go.write(f"model={mod}\n")
                        go.write(f"skip=false\n")
                        go.write(f"reason=role={role} gemini={mod} used={new_used}/{limit} (ranked score={candidate['score']}) residual\n")
                return

            sys.stderr.write(f"Gemini residual soft budget exhausted: {mod} ({used}/{limit})\n")

    # 6. All free options exhausted
    print(f"::set-output name=provider::none")
    print(f"::set-output name=model::")
    print(f"::set-output name=skip::true")
    print(f"::set-output name=reason::all free paths exhausted (omni/openrouter peers + gemini residual) role={role}")

    if "GITHUB_OUTPUT" in os.environ:
        with open(os.environ["GITHUB_OUTPUT"], "a") as go:
            go.write(f"provider=none\n")
            go.write(f"model=\n")
            go.write(f"skip=true\n")
            go.write(f"reason=all free paths exhausted (omni/openrouter peers + gemini residual) role={role}\n")


if __name__ == "__main__":
    main()
