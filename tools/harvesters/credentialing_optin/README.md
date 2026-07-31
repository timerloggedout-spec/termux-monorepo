# Harvesters: Credentialing (OPT-IN ONLY)

This folder contains scripts that interact with browser instances or attempt to extract session
artifacts (cookies, bearer tokens) from a running browser. These scripts are sensitive and must
be treated as PRIVATE, opt-in tools.

Rules
- DO NOT run any script in this directory unless you explicitly opt-in.
- Each script must present an interactive consent prompt before performing any credential operations.
- Scripts will be run only in a secure, trusted environment under operator control.
- Scripts write any captured tokens to the directory configured in `archwiz/config.py` (defaults to `~/.multi-ai-tokens`) and will set file permissions to 600.

If you need help converting a parser into an opt-in credential capture tool, consult the security
team or the repository owner.
