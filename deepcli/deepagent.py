#!/usr/bin/env python3
"""deepagent.py — agent loop with DIRECT imports, no HTTP hop.

Same tool semantics as agent.py, but:
- imports deepcli.core, gh_broker, files/skills logic in-process
- doesn't need server.py running
- server.py stays for external callers (GH Actions, Agora, curl)
"""
