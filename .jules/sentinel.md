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

## 2026-08-16 - Cross-Platform Path Traversal and Symlink Hijacking Prevention in Session Configuration
**Vulnerability:** Unsanitized token path strings and unvalidated symlinks in `multi-ai-cli/core/session_manager.py` could allow malicious config settings or symlinks to read arbitrary files from the filesystem when loading credentials.
**Learning:** Naive string checks for directory separators like `\\` break cross-platform compatibility on Windows where `\\` is a standard path separator. Using `Path(token_str).parts` allows checking for `..` path components safely across OS platforms without false positives.
**Prevention:** Validate `".." in Path(token_str).parts` for path traversal detection, and verify `Path(p).is_symlink()` before opening user configuration or token files.

## 2026-08-17 - Symlink Hijacking and Path Traversal Prevention in Patch Routers
**Vulnerability:** In `harmony_hub/src/patch_router.py`, `apply_patch` allowed arbitrary targets without path traversal validation (`..`) or symlink checks, enabling attackers or crafted patches to overwrite system or sensitive files outside the workspace. In addition, temporary python patch execution scripts were created with default umask permissions and unvalidated symlink checks.
**Learning:** Utilities that accept patch files or target file paths must enforce strict validation against symlink targets and path traversal before invoking script processes. Creating temporary execution files without restricted permissions (`0o600`) or symlink guards allows local privilege escalation or arbitrary script injection.
**Prevention:** Validate `".." not in target_path.parts`, enforce `not target_path.is_symlink()`, write temporary scripts with `os.open` mode `0o600`, and clean up temporary execution scripts securely inside a `finally` block.

## 2026-09-09 - Symlink Hijacking Prevention in Activity Listener Script Sandbox
**Vulnerability:** In `archwiz/activity_listener.py`, auto-executed code block scripts written into `SANDBOX` ran `script.chmod(0o755)` without checking whether `script` was a symlink, allowing local symlink hijacking.
**Learning:** Creating temporary execution scripts in shared or local user directories without verifying `is_symlink()` allows local users to pre-create symlinks pointing to sensitive system files, causing `chmod` or `write_text` to modify permissions on unexpected target files.
**Prevention:** Always check `script.is_symlink()` before writing or executing temporary scripts, and wrap top-level polling loops in `if __name__ == '__main__':` to allow safe test module imports.
