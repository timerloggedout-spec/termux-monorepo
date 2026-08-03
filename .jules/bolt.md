# Bolt's Performance Journal

Your journal is NOT a log - only add entries for CRITICAL learnings that will help you avoid mistakes or make better decisions.

## 2026-08-01 - Immutable Content-Addressed Storage (CAS) and Decoupling Indexes
**Learning:**
Standardizing on an immutable content-addressed storage (CAS) hierarchy (`blob/sha256/ab/abcd...`) using full SHA-256 hashes instead of truncated hashes ensures absolute uniqueness and zero duplication of file content blocks across multiple conversation sessions.
By representing conversation pointers with explicit provenance metadata (`provider`, `account`, `session`, `message`, `block`, `content_hash`) while maintaining backward-compatible `@property` and legacy positional mappings in `Pointer`, we can seamlessly migrate complex schemas with zero runtime regressions.

**Action:**
Always design index pointers to reference content-addressed file hashes rather than writing duplicate files per session. Implement robust positional and keyword attribute mappings in constructors to enable safe backward compatibility during API upgrades.
