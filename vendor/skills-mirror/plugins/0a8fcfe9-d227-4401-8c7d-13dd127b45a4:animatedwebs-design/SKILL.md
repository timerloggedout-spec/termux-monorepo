---
name: animatedwebs-design
description: "Connect and use AnimatedWebs Design Studio, the private design workspace with built-in AI, from Claude Code. Use when the user wants to explore design directions, create design projects or artifacts, or asks to open or connect AnimatedWebs Design."
---

# AnimatedWebs Design Studio

1. **Get the workspace.** Call `get_account` with `includeDesignConnect` true and read its `design` section. It returns the user's private workspace link, the Design AI allowance (`designAi`) and a one-line setup for the Design Studio MCP server in Claude Code, Cursor and VS Code.
2. **Connect it.** Offer to run the Claude Code setup command it returns, so Design Studio tools become available in this session. The token in that command is personal: never commit it or paste it into shared files.
3. **Usage.** Free accounts include a daily AI allowance and Pro raises it. Users can also add their own API key in Design Studio settings.
