# Security and responsible use

This repository contains helpers that interact with external Web chat providers (e.g., Mistral).
Some tools in the repository are convenience scripts for local use only and may read or write
sensitive artifacts such as cookies, bearer tokens, or session exports.

Guidelines
- Do NOT commit tokens, cookie files, session exports, or other credentials into the repository.
- Any script that interacts with credentials must be run deliberately by an operator, and only
  after they have reviewed the code and understand the legal and ToS implications.
- Tools that capture or manipulate credentials are placed under tools/harvesters/credentialing_optin/
  and require explicit opt-in (see README in that folder).
- Token files, cookie files, and session exports MUST use 600 permissions; directories MUST use 700 permissions.

If you find secrets accidentally committed to the repo, follow the GitHub guidance for removing
secrets from history and rotate the credentials immediately.
