## 2026-08-12 - Local Privilege Restrictions & Symlink Hijacking Prevention
**Vulnerability:** Weak default file permissions on user configurations (`~/.deepcli/config.json`) and session logs, which could allow unauthorized local users to access highly sensitive credentials (like `DEEPSEEK_TOKEN` and session cookies) on multi-user environments.
**Learning:** Default file and directory creation permissions (umask) can leave configuration files readable by other local users. Furthermore, applying recursive permission adjustments without skipping symlinks can expose the application to traversal hijacking vulnerabilities if a malicious user links a sensitive system file inside the user's config folder.
**Prevention:** Explicitly restrict sensitive configuration/cache directories to `0o700` and files to `0o600`. Secure all permission adjustments by validating that target paths are not symlinks (`path.is_symlink()`) before calling chmod.

## 2026-08-13 - Path Traversal Prevention in Local Session Storage Cache Paths
**Vulnerability:** Path traversal vulnerability via unvalidated/unsanitized input in session_id when constructing the local cache path (`_cache_path`), potentially allowing attackers to read or write files outside of the intended `.deepcli/session_store` sandbox directory structure.
**Learning:** Even internal utility functions like cache path builders should enforce strict input validation (allow-listing or strict character filtering) and layout boundary checks (via real path alignment check with `os.path.commonpath`) to prevent path traversal vectors.
**Prevention:** Always sanitize the filename components by retaining only safe alphanumeric/selected special characters and strictly validating the canonical path alignment against the expected base directory.

## 2026-08-14 - Session Key Collision and Header Pollution in Shared HTTP Sessions
**Vulnerability:** Key collision in `get_session` caused by truncating bearer tokens to 20 chars, causing distinct accounts sharing prefix strings to reuse the same cached `Session` instance. In addition, direct mutation of `s.headers` with one-shot `X-Ds-Pow-Response` headers polluted subsequent requests on shared sessions.
**Learning:** Naive string truncation for dictionary keys creates subtle collision risks across distinct credentials. Mutating persistent `Session.headers` directly for single-use headers leaks authentication/challenge tokens across unrelated API requests.
**Prevention:** Use SHA-256 digests over full token and cookie pairs to generate session cache keys (`_session_cache_key`), and always construct request-scoped header dictionaries without mutating shared session instances.

## 2026-08-15 - Path Traversal Containment in Local Bridge Servers
**Vulnerability:** Unsanitized working directory (`cwd`) parameter accepted in HTTP request payloads in `bin/obsidian_server.py`, allowing callers to execute shell commands outside the intended `$HOME` directory sandbox boundary.
**Learning:** Accepting client-specified working directory paths in local bridge HTTP handlers without realpath resolution and base boundary checks allows arbitrary filesystem traversal. In addition, importing top-level server scripts that execute server loops immediately on import hinders automated test isolation.
**Prevention:** Always resolve paths with `os.path.realpath` and enforce `os.path.commonpath([base_dir, resolved_path]) == base_dir` validation. Always wrap server execution entrypoints in `if __name__ == '__main__':`.
