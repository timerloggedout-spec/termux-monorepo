"""
Routing logic for provider selection: OpenRouter, Omni, DeepSeek web.
All are peers; selection based on cost, latency, and availability.
"""
import os
import random

# Simple scoring: lower is better
def score_provider(provider, env):
    if provider == 'openrouter':
        return 10 if env.get('OPENROUTER_API_KEY') else 999
    elif provider == 'omni':
        return 15 if env.get('OMNI_API_KEY') else 999
    elif provider == 'deepseek':
        # Web wrapper – always available but may be slower/rate-limited
        return 20
    return 999

def select_peer(event, env=None):
    """
    Returns a dict with 'provider', 'endpoint', and 'api_key'.
    """
    if env is None:
        env = os.environ

    # Get list of available providers with scores
    providers = [
        {
            'name': 'openrouter',
            'score': score_provider('openrouter', env),
            'endpoint': 'https://openrouter.ai/api/v1/chat/completions'
        },
        {
            'name': 'omni',
            'score': score_provider('omni', env),
            'endpoint': env.get('OMNI_BASE_URL', 'https://api.omni.ai/v1/chat/completions')
        },
        {
            'name': 'deepseek',
            'score': score_provider('deepseek', env),
            'endpoint': None
        },  # web wrapper
    ]

    # Filter out unavailable
    available = [p for p in providers if p['score'] < 100]

    if not available:
        raise RuntimeError("No providers available")

    # Weighted random (lower score = higher weight)
    # We'll pick the best with some randomness for load balancing
    best = min(available, key=lambda p: p['score'])
    # Add jitter: if score difference < 5, pick randomly among top 2
    sorted_providers = sorted(available, key=lambda p: p['score'])
    if len(sorted_providers) > 1 and sorted_providers[1]['score'] - sorted_providers[0]['score'] < 5:
        chosen = random.choice(sorted_providers[:2])
    else:
        chosen = best

    return {
        'provider': chosen['name'],
        'endpoint': chosen.get('endpoint'),
        'api_key': env.get(f"{chosen['name'].upper()}_API_KEY", None),
    }
