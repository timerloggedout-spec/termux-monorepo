---
name: lapyn
description: Operate an authorized Lapyn design through Code Mode MCP, or diagnose connection failures. Do not use for ordinary repository work or generic debugging.
---

# Lapyn

This skill ships with Lapyn plugin `0.3.0`. Lapyn designs are read and edited by running JavaScript against the Lapyn SDK with the `code` tool, and saved screens are rendered with the `render` tool; `sdk_reference` is that SDK's documentation.

1. Before your first `code` call in a session, call `sdk_reference` without a topic and with `plugin: "0.3.0"`. It returns an overview of the SDK and its topic list. If it reports that the plugin is outdated, tell the user once how to update it.
2. Before writing code, look up the topics or groups your code uses, such as `props.layout`, `props` or `drafts`, for their exact signatures and usage notes.
3. Run the JavaScript with the `code` tool.

Use the MCP endpoint the plugin configures; never substitute or probe another environment. SDK changes never need a reconnect: a fingerprint mismatch error says how to continue. Reconnect or reauthorize only when the credential expired or was revoked.
