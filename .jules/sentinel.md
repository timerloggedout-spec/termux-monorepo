## 2026-08-12 - Local Privilege Restrictions & Symlink Hijacking Prevention
**Vulnerability:** Weak default file permissions on user configurations (`~/.deepcli/config.json`) and session logs, which could allow unauthorized local users to access highly sensitive credentials (like `DEEPSEEK_TOKEN` and session cookies) on multi-user environments.
**Learning:** Default file and directory creation permissions (umask) can leave configuration files readable by other local users. Furthermore, applying recursive permission adjustments without skipping symlinks can expose the application to traversal hijacking vulnerabilities if a malicious user links a sensitive system file inside the user's config folder.
**Prevention:** Explicitly restrict sensitive configuration/cache directories to `0o700` and files to `0o600`. Secure all permission adjustments by validating that target paths are not symlinks (`path.is_symlink()`) before calling chmod.

## 2026-08-13 - Path Traversal Prevention in Local Session Storage Cache Paths
**Vulnerability:** Path traversal vulnerability via unvalidated/unsanitized input in session_id when constructing the local cache path (`_cache_path`), potentially allowing attackers to read or write files outside of the intended `.deepcli/session_store` sandbox directory structure.
**Learning:** Even internal utility functions like cache path builders should enforce strict input validation (allow-listing or strict character filtering) and layout boundary checks (via real path alignment check with `os.path.commonpath`) to prevent path traversal vectors.
**Prevention:** Always sanitize the filename components by retaining only safe alphanumeric/selected special characters and strictly validating the canonical path alignment against the expected base directory.
