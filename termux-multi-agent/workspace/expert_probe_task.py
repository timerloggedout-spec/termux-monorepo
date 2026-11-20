"""
Investigation task: Find the correct version header to unlock Expert model.
Strategies:
  - header-brute: brute-force common version patterns
  - js-extract: parse the web JS bundle for version strings
  - wasm-reverse: extract version gate from deepseek.wasm via strings
  - mitm-sniff: capture real browser headers (needs mitmproxy working)
Success criterion: chat_completion returns non-"Update to latest version" response.
"""
TASK = "expert_version_unlock"
