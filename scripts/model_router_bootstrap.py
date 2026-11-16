#!/usr/bin/env python3
"""Entry used by model-router action: live catalog feeds peers before legacy path.

Delegates to scripts.model_router after injecting live peers via env + feed side-channel.
"""
from __future__ import annotations

import os
import sys


def main() -> int:
    # Ensure secret presence flips HAS_* for catalog + peer selection
    if os.environ.get("OPENROUTER_API_KEY"):
        os.environ["HAS_OPENROUTER"] = "true"
    if os.environ.get("FELO_AI_API"):
        os.environ["HAS_FELO"] = "true"
    if os.environ.get("OMNI_API_KEY") or os.environ.get("OMNIROUTE_API_KEY"):
        os.environ["HAS_OMNI"] = "true"

    # Prefetch live catalog into COUNTER_DIR so model_router can import feed
    try:
        from scripts import live_catalog_feed

        providers = []
        if os.environ.get("HAS_OPENROUTER", "").lower() == "true":
            providers.append("openrouter")
        if os.environ.get("HAS_FELO", "").lower() == "true":
            providers.append("felo")
        if os.environ.get("HAS_OMNI", "").lower() == "true":
            providers.append("omni")
        feed = live_catalog_feed.load_eligible(providers=providers or None)
        os.environ["LIVE_CATALOG_STATE"] = str(feed.get("catalog_state") or "unavailable")
        # Encode top peers for model_router extension point
        peers = live_catalog_feed.peer_candidates_for_role(os.environ.get("ROLE", "triage"), feed)
        os.environ["LIVE_CATALOG_PEERS"] = ",".join(f"{p}/{m}" for p, m in peers[:24])
        print(
            f"catalog_feed state={feed.get('catalog_state')} eligible={len(feed.get('eligible') or [])} "
            f"peers={len(peers)} states={feed.get('provider_states')}",
            file=sys.stderr,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"catalog_feed unavailable: {exc}", file=sys.stderr)
        os.environ.setdefault("LIVE_CATALOG_STATE", "unavailable")

    from scripts import model_router as mr

    # Monkey-patch ROLE_PEERS for this process: prepend live peers
    role = os.environ.get("ROLE", "triage")
    raw = os.environ.get("LIVE_CATALOG_PEERS") or ""
    live = []
    for item in raw.split(","):
        item = item.strip()
        if not item or "/" not in item:
            continue
        provider, model = item.split("/", 1)
        live.append((provider, model))
    if live:
        base = list(mr.ROLE_PEERS.get(role, []))
        merged = []
        seen = set()
        for pair in live + base:
            if pair not in seen:
                seen.add(pair)
                merged.append(pair)
        mr.ROLE_PEERS = dict(mr.ROLE_PEERS)
        mr.ROLE_PEERS[role] = merged

    mr.main()
    # surface catalog state for action output
    state = os.environ.get("LIVE_CATALOG_STATE", "unavailable")
    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a", encoding="utf-8") as fh:
            fh.write(f"catalog_state={state}\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
