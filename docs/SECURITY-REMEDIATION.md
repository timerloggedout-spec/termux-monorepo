# Security Remediation Sequence (PR #3 lineage)

> **Status:** REQUIRED before treating session-store work as done  
> Related: `agent/repository-hygiene`, Critical-Eval §4, repo-gate HARD rules

## Three independent guarantees

| | Guarantee | PR #3 today |
|---|-----------|-------------|
| **A** | Current tree is clean | Partially addressed (tip removal) |
| **B** | Future commits cannot reintroduce secrets | Partially (gitignore + gate path bans) |
| **C** | Historical reachable objects remediated | **Not done** |

> branch-tip removal ≠ history remediation

## P0 sequence

1. **Rotate** any credential that ever appeared in tracked session material
   (API keys, cookies, tokens, browser profile data).
2. **Verify** current `master` and all surviving integration branches are
   free of Class 3/4 paths in the *tree* (not only HEAD of one branch).
3. **Keep** secret-pattern + path-class checks in repo-gate (already live):
   - `.deepcli/session_store`, `.pi`, `.synthegration`
   - browser profiles / Cookies / Local State
   - high-confidence key patterns
4. **Expand** path-class prohibitions as needed (Class 0–4 model).
5. **History rewrite** only after deliberate export/preservation of old
   history for forensics if required.
6. **Force-push** only with explicit operator approval and coordinated
   branch updates (all open PRs must retarget).

## Data classification (gate target)

| Class | Content | Gate |
|-------|---------|------|
| 0 | Source, docs, schemas | allow |
| 1 | Derived indexes, hashes | allow + generated marker |
| 2 | Conversation content, local paths, prompts | explicit allowlist |
| 3 | Cookies, auth headers, session stores, tokens | **HARD FAIL** |
| 4 | Browser profiles, private SSH, local env | **HARD FAIL** |

## Do not

- Mistake a green working tree for eradicated credentials
- Merge large multi-AI branches while Class 3/4 history is still reachable
  without a remediation plan
- Commit recovery dumps of session material "for later"

## Operator checklist (copy)

- [ ] Credentials rotated
- [ ] Tip of master-staging clean under repo-gate
- [ ] Open branches scanned for Class 3/4 paths
- [ ] History rewrite plan written and reviewed
- [ ] Preservation archive stored offline if needed
- [ ] Force-push window coordinated
- [ ] Downstream clones notified to re-clone / reset
