# Sentinel's Security Journal

Your journal is NOT a log - only add entries for CRITICAL security learnings.

## 2026-08-05 - Symlink-Safe Local Directory Permission Restricting (0o700 / 0o600)
**Vulnerability:**
Local files and directories storing sensitive credentials (like Bearer tokens), user profile cookie databases (like browser-data), session exports (cache files), and sqlite database records (`local_repo.db`) were created using default system umask, making them potentially world-readable/group-readable (e.g. `0o644`/`0o755`). This represents a local exposure threat where other users on a shared environment (such as Termux on a shared/multi-user system) could access active session states.

**Learning:**
Explicitly modifying file/directory permissions to `0o600` and `0o700` is an essential local containment practice. However, recursive permission changes are vulnerable to symlink hijacking/arbitrary file permission modification if they blindly traverse directory paths. To prevent path traversal/symlink exploits, recursive permission modifications must explicitly skip symlinks (`path.is_symlink()`) and wrap `chmod` calls inside a protective try-except block to handle restricted or read-only filesystems (like FAT32 or certain containerized/headless virtual mounts) gracefully.

**Prevention:**
Always use a symlink-safe recursive walker when locking down user data folders, explicitly securing directories with `0o700` and files with `0o600`. Apply `try...except` isolation around all `os.chmod` or `Path.chmod` calls to fail-securely and prevent runtime crashes.
