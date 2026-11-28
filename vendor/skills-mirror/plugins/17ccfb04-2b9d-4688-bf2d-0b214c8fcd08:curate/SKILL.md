---
description: Discover external agents, skills, or MCP servers that could improve the plugin's capabilities for the current task. Searches the web, presents candidates, adds approved ones to the registry. Never mutates without user approval.
argument-hint: "[topic or recent task]"
allowed-tools: WebSearch, WebFetch, Read, Write, Edit, Bash, Glob, Grep
destructive: true
read-only: false
---

Invoke the **curator** skill:

/one-shot-prompting:curator $ARGUMENTS

The curator runs `agent_discovery.py` to see what we already have, then
WebSearches Anthropic-trusted sources for external candidates. It presents
candidates with strengths + risks; you approve or reject by number; on
approval, the candidate is appended to `.claude/registry/`.

This is how the plugin teaches itself new capabilities across sessions.
