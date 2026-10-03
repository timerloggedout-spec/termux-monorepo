"""_v1_preflight — three-detector risk scoring for session events.

Given a stream of symbolic events (from _v1_events), predict whether
a destructive action is about to be taken without a recovery path.

Detectors:
  A. penalty_count  — weighted sum over recent window
  B. pattern_match  — known dangerous n-grams with probabilities
  C. env_state      — current system state (agent grips, pubring size)

Combined into a GREEN / AMBER / RED level for a candidate action.

Public API:
    score(events, next_action=None) -> dict
    env_state() -> dict             # live system probe
    check_action(action) -> dict    # preflight for a single action
"""

import os, re, json, time, pathlib, subprocess

HOME = pathlib.Path.home()

# ─── weights ──────────────────────────────────────────────────
PENALTY = {
    "KILL_AGENT":          10,
    "PUBRING_DELETE":      12,
    "PRIVATE_KEY_DELETE":  12,
    "CRED_WRITE":           8,
    "CRED_READ":            3,
    "AGENT_CACHED":         2,
    "PUBRING_EMPTY":        3,
    "TOTP_FAIL":            1,
}

# ─── known dangerous sequences ────────────────────────────────
# p = P(failure follows | this n-gram observed)
DANGER_NGRAMS = {
    ("KILL_AGENT", "TOTP_CALL"):        0.95,
    ("KILL_AGENT", "AGENT_EMPTY"):      0.90,
    ("CRED_READ", "KILL_AGENT"):        0.85,
    ("KILL_AGENT", "KILL_AGENT"):       0.70,
    ("PUBRING_EMPTY", "KILL_AGENT"):    0.92,
    ("PUBRING_DELETE", "KILL_AGENT"):   0.95,
}

DESTRUCTIVE_ACTIONS = {
    "KILL_AGENT", "CRED_WRITE", "PUBRING_DELETE", "PRIVATE_KEY_DELETE"
}


def penalty_count(events, window=10):
    score = 0
    for e in events[-window:]:
        score += PENALTY.get(e, 0)
    return score


def pattern_match(events, window=20):
    recent = events[-window:]
    best = 0.0
    best_gram = None
    for n in (2, 3, 4):
        for i in range(len(recent) - n + 1):
            gram = tuple(recent[i:i+n])
            p = DANGER_NGRAMS.get(gram, 0)
            if p > best:
                best = p
                best_gram = gram
    return best, best_gram


def env_state():
    """Live probe of the GPG/agent environment. Stdlib only."""
    out = {
        "agent_grips":      0,
        "pubring_size":     0,
        "pass_2fa_exists":  False,
        "agent_running":    False,
    }
    # agent grips
    try:
        r = subprocess.run(
            ["gpg-connect-agent", "KEYINFO --list", "/bye"],
            capture_output=True, text=True, timeout=5)
        grips = re.findall(r"S KEYINFO ([0-9A-F]{40})", r.stdout)
        out["agent_grips"] = len(grips)
        out["agent_running"] = "OK" in r.stdout or len(grips) > 0
    except Exception:
        pass
    # pubring size
    pub = HOME / ".gnupg" / "pubring.kbx"
    if pub.exists():
        try: out["pubring_size"] = pub.stat().st_size
        except Exception: pass
    # passphrase file
    out["pass_2fa_exists"] = (HOME / ".gnupg" / ".2fa-pass").exists()
    return out


def env_risk(state=None):
    state = state or env_state()
    weights = {
        "agent_empty":      5 if state["agent_grips"] == 0 else 0,
        "pubring_empty":    4 if state["pubring_size"] < 100 else 0,
        "pass_2fa_missing": 8 if not state["pass_2fa_exists"] else 0,
    }
    return sum(weights.values()), weights


def score(events, next_action=None, env=None):
    """Return dict with level GREEN/AMBER/RED and reason."""
    p_score, p_gram = pattern_match(events)
    e_score = penalty_count(events)
    env_score, env_weights = env_risk(env)

    result = {
        "level": "GREEN",
        "reason": "",
        "penalty": e_score,
        "pattern_p": p_score,
        "pattern_gram": list(p_gram) if p_gram else None,
        "env_score": env_score,
        "env_weights": env_weights,
        "next_action": next_action,
    }

    # if environment is already fragile and next action is destructive → RED
    if next_action in DESTRUCTIVE_ACTIONS and env_score >= 12:
        result["level"] = "RED"
        result["reason"] = f"fragile env ({env_weights}) + {next_action} is irreversible"
        return result

    # destructive on a cached-but-unrecoverable agent
    if next_action == "KILL_AGENT" and env.get("pubring_size", 0) < 100 and env.get("agent_grips", 0) > 0:
        result["level"] = "RED"
        result["reason"] = "KILL_AGENT on cached agent with empty pubring — no recovery"
        return result

    # pattern match
    if p_score >= 0.90:
        result["level"] = "RED"
        result["reason"] = f"known-dangerous n-gram {p_gram} p={p_score:.2f}"
        return result
    if p_score >= 0.80:
        result["level"] = "AMBER"
        result["reason"] = f"suspicious n-gram {p_gram} p={p_score:.2f}"
        return result

    # penalty threshold
    if e_score >= 18:
        result["level"] = "RED"
        result["reason"] = f"cumulative penalty {e_score}"
        return result
    if e_score >= 13:
        result["level"] = "AMBER"
        result["reason"] = f"cumulative penalty {e_score}"
        return result

    return result


def check_action(action, env=None):
    """Preflight a single candidate action.

    Thin, documented wrapper over ``score()``: the action itself is folded
    into the event stream so the penalty and n-gram detectors see it, and a
    live environment probe is used unless ``env`` is supplied. Returns the
    same dict as ``score()`` with two extra keys:

        action : the action that was checked
        safe   : True when the level is GREEN
    """
    result = score([action], next_action=action, env=env)
    result["action"] = action
    result["safe"] = result["level"] == "GREEN"
    return result
