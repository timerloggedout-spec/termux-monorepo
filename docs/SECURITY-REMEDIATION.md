# Security Remediation Sequence (PR #3 lineage)

> **Status:** REQUIRED before treating session-store work as done

## Three independent guarantees

| | Guarantee | PR #3 today |
|---|-----------|-------------|
| **A** | Current tree is clean | Partially (tip removal) |
| **B** | Future commits cannot reintroduce secrets | Partially (gitignore + gate) |
| **C** | Historical reachable objects remediated | **Not done** |

> branch-tip removal ≠ history remediation

## P0 sequence

1. **Rotate** credentials that appeared in tracked session material
2. **Verify** tips free of Class 3/4 paths
3. **Keep** secret-pattern + path-class checks in repo-gate
4. **History rewrite** only after deliberate export if required
5. **Force-push** only with explicit Operator approval

## Data classification

| Class | Content | Gate |
|-------|---------|------|
| 0 | Source, docs, schemas | allow |
| 1 | Derived indexes, hashes | allow |
| 2 | Conversation content, prompts | allowlist |
| 3 | Cookies, session stores, tokens | **HARD FAIL** |
| 4 | Browser profiles, private SSH, local env | **HARD FAIL** |
