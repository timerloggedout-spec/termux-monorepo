# Sentinel's Security Journal

Your journal is NOT a log - only add entries for CRITICAL security learnings.

## 2026-08-09 - Local Privilege Permission Profiles and Path Traversal in DeepCLI Configuration & Session Cache
**Vulnerability:**
The `deepcli` package stored user Bearer tokens (sensitive credentials) and session histories (containing potentially private prompt contents) in standard directories without explicitly restricting access permissions. This allowed other local users on a multi-user system to read the config and cache files. Additionally, the cache and upload utilities accepted custom inputs without validating path components, leaving them vulnerable to path traversal.

**Learning:**
On multi-user systems (like standard Linux or shared developer servers), credentials, configurations, and exports must be protected by setting tight file permissions (`0o600` for files containing credentials, tokens, or exports, and `0o700` for their parent directories). Path utilities (such as upload or cache resolvers) must explicitly reject components with path traversals (like `..`) to prevent traversal hijacking vulnerabilities.

**Prevention:**
1. Explicitly invoke `CONFIG_DIR.chmod(0o700)` or equivalent when initializing config directories.
2. Ensure files containing tokens, cookies, or history data are created or saved with `0o600` permissions.
3. Validate and sanitize paths derived from user/API-supplied inputs to block relative traversal patterns (`..`).
