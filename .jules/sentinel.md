# Sentinel's Security Journal

## 2026-08-01 - Config Directory Permission Leakage and Local Privilege Restrictions
**Vulnerability:** Session tokens, API keys, and chat logs were written to the user's home directory (`~/.deepcli/`) without strict permissions, leaving them readable by other local users on a multi-user system.
**Learning:** Standard file and directory creation methods (`Path.mkdir()` and `open('w')`) in Python use the system default umask (typically `0o022` or `0o002`), making directories world/group-readable (`0o755` or `0o775`) and files group/world-readable (`0o644` or `0o664`). To conform with strict security requirements (like `SECURITY.md`), credentials and session stores must use explicit `0o700` (directories) and `0o600` (files) permissions.
**Prevention:** Wrap file and directory creation with explicit `chmod(0o700)` and `chmod(0o600)` calls. Encase these chmod calls in try-except blocks to maintain portability on filesystems/OSes that don't support POSIX modes.
