## 2026-08-12 - Local Privilege Restrictions & Symlink Hijacking Prevention
**Vulnerability:** Weak default file permissions on user configurations (`~/.deepcli/config.json`) and session logs, which could allow unauthorized local users to access highly sensitive credentials (like `DEEPSEEK_TOKEN` and session cookies) on multi-user environments.
**Learning:** Default file and directory creation permissions (umask) can leave configuration files readable by other local users. Furthermore, applying recursive permission adjustments without skipping symlinks can expose the application to traversal hijacking vulnerabilities if a malicious user links a sensitive system file inside the user's config folder.
**Prevention:** Explicitly restrict sensitive configuration/cache directories to `0o700` and files to `0o600`. Secure all permission adjustments by validating that target paths are not symlinks (`path.is_symlink()`) before calling chmod.

## 2026-08-13 - Command Injection in MCP Server Tool Execution
**Vulnerability:** Command injection via shell metacharacters (e.g. `;`, `&&`, `$()`) in parameters like `--schema`, `--input`, and `code` passed to Node's `execSync` inside `cedar-mcp-server.js`.
**Learning:** Using `execSync` with template literal string interpolation evaluates parameters within a shell environment, allowing malicious inputs to execute arbitrary code or shell instructions. Additionally, unhandled command failures in the main loop can cause the entire MCP server process to crash.
**Prevention:** Always use `execFileSync` or pass arguments strictly as an array to ensure they are treated as literal arguments instead of shell instructions. Wrap execution steps in robust error handling to return failures gracefully without crashing.
