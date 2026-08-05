# SKYHOOK Development Workflow

**Agent:** Mistral-Vibe
**Profile:** Mistral-Vibe
**Signed-off-by:** Mistral-Vibe <mistral-vibe@mistral.ai>

One for All; and, All for One!

---

## Branch Strategy

### Branch Hierarchy

```
┌─────────────────────────────────────────────────────────────┐
│                    BRANCH FLOW                                │
├─────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌─────────────────┐     ┌─────────────────┐                 │
│  │   feature/       │────▶│   vibe/          │                 │
│  │   skyhook        │     │   skyhook-       │                 │
│  │   (Grok's work)  │     │   integration-   │                 │
│  └─────────────────┘     │   8475f1         │                 │
│                            │   (Mistral-Vibe) │                 │
│                            └────────┬────────┘                 │
│                                             │                     │
│                    ┌────────────────────────┼─────────────┐  │
│                    │                        │                 │  │
│                    ▼                        ▼                 │  │
│           ┌─────────────────┐    ┌─────────────────┐          │  │
│           │  termux-smoke    │    │  master-staging  │          │  │
│           │  (Testing)       │    │  (Staging)       │          │  │
│           └─────────────────┘    └────────┬────────┘          │  │
│                                            │                    │  │
│                    ┌────────────────────────┼─────────────┐  │
│                    │                        │                 │  │
│                    ▼                        ▼                 │  │
│           ┌─────────────────┐    ┌─────────────────┐          │  │
│           │  master          │◀───│  (Production)     │          │  │
│           │  (Stable)        │    └─────────────────┘          │  │
│           └─────────────────┘                                    │  │
│                                                                  │
└─────────────────────────────────────────────────────────────┘
```

### Branch Descriptions

| Branch | Purpose | Status | Merge Target |
|--------|---------|--------|--------------|
| `feature/skyhook` | Grok's original SKYHOOK work | Active | termux-smoke |
| `vibe/skyhook-integration-8475f1` | Mistral-Vibe's integration work | Active | termux-smoke |
| `termux-smoke` | Testing branch for Termux compatibility | Active | master-staging |
| `master-staging` | Production-ready staging | Active | master |
| `master` | Stable production | Protected | N/A |

### Workflow Rules

1. **Feature Development**
   - Each agent (Grok, Mistral-Vibe, etc.) works in their own feature branch
   - Feature branches run parallel as separate trunks
   - No direct commits to `termux-smoke` or `master-staging`

2. **Testing Phase**
   - Feature branches are merged to `termux-smoke` for testing
   - `termux-smoke` is the integration testing branch
   - All Termux-specific testing happens here

3. **Staging Phase**
   - After successful testing in `termux-smoke`, PRs are created to `master-staging`
   - `master-staging` contains production-ready code
   - Final integration testing happens here

4. **Production Phase**
   - `master-staging` is merged to `master` for production deployment
   - `master` is protected and only receives merges from `master-staging`

---

## Development Process

### For Mistral-Vibe (This Agent)

1. **Create Feature Branch**
   ```bash
   git checkout -b vibe/<feature-name>-<timestamp>
   ```

2. **Develop Features**
   - Implement new functionality
   - Add comprehensive tests
   - Update documentation
   - Sign all commits as Mistral-Vibe

3. **Test Locally**
   ```bash
   # Run protocol layer tests
   python -m unittest skyhook.tests.test_protocol -v
   
   # Test device optimization
   python -c "from skyhook.device import get_resource_monitor; print(get_resource_monitor().get_status())"
   
   # Test orchestration
   python -c "from skyhook.orchestration import get_agent_registry; print(len(get_agent_registry().get_available_agents()))"
   ```

4. **Create PR to termux-smoke**
   ```bash
   # Push feature branch
   git push origin vibe/<feature-name>-<timestamp>
   
   # Create PR to termux-smoke
   gh pr create --base termux-smoke --head vibe/<feature-name>-<timestamp>
   ```

5. **After Testing in termux-smoke**
   - Monitor CI/CD results
   - Fix any issues
   - Get approvals from collaborators

6. **Create PR to master-staging**
   ```bash
   # Create PR from termux-smoke to master-staging
   gh pr create --base master-staging --head termux-smoke
   ```

---

## Collaboration Guidelines

### Separation of Concerns

- **Grok** (xAI): Focuses on agent orchestration and Jules integration
- **Mistral-Vibe**: Focuses on protocol layer, device optimization, and integration
- **Other Agents**: Each has their own focus areas

### Branch Naming Convention

| Agent | Branch Prefix | Example |
|-------|---------------|---------|
| Grok | `feature/` | `feature/skyhook` |
| Mistral-Vibe | `vibe/` | `vibe/skyhook-integration-8475f1` |
| CodeRabbit | `coderabbit/` | `coderabbit/autofix` |
| Devin | `devin/` | `devin/automation` |

### Commit Signing

Each agent MUST sign their own work:

```
Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>

One for All; and, All for One!
```

**NOT:**
```
Agent: Grok | Jules  # This is Grok's signature
Profile: https://x.com/grok  # This is Grok's profile
Signed-off-by: Grok <grok@x.ai>  # This is Grok's signature
```

---

## Splicing Strategy

### What is Splicing?

Splicing is the process of selectively merging specific commits or features from one branch to another without merging the entire branch history.

### When to Splice

1. **Selective Feature Integration**
   - When only specific features from a branch are needed
   - When a branch contains multiple unrelated changes

2. **Parallel Development**
   - When multiple agents are working on different features
   - When features need to be integrated independently

3. **Experimental Features**
   - When testing experimental features in isolation
   - When features need gradual rollout

### How to Splice

#### Method 1: Cherry-Pick
```bash
# Cherry-pick specific commits
git checkout target-branch
git cherry-pick <commit-hash>
```

#### Method 2: Merge with Strategy
```bash
# Merge specific files
git checkout target-branch
git checkout source-branch -- path/to/file1 path/to/file2
git commit -m "Splice: Add specific files from source-branch"
```

#### Method 3: Patch Application
```bash
# Create patch from source branch
git checkout source-branch
git format-patch -1 <commit-hash> --stdout > feature.patch

# Apply patch to target branch
git checkout target-branch
git apply feature.patch
```

---

## Current Branch Status

### Active Branches

1. **`feature/skyhook`** (Grok)
   - Status: Active
   - Purpose: Original SKYHOOK framework
   - Next: Merge to termux-smoke

2. **`vibe/skyhook-integration-8475f1`** (Mistral-Vibe)
   - Status: Active (Current)
   - Purpose: Integration framework with protocol layer, device optimization, orchestration
   - Features:
     - Protocol layer (16 files, 29 tests)
     - Device optimization (8 files)
     - Orchestration (4 files)
     - Antigravity interface (5 files)
     - Documentation (6 files)
   - Next: PR to termux-smoke

3. **`termux-smoke`**
   - Status: Active
   - Purpose: Testing branch for Termux compatibility
   - Next: PR to master-staging

4. **`master-staging`**
   - Status: Active
   - Purpose: Production-ready staging
   - Next: PR to master

5. **`master`**
   - Status: Protected
   - Purpose: Stable production
   - Next: N/A (only receives from master-staging)

---

## Merge Strategy

### From vibe/skyhook-integration-8475f1 to termux-smoke

1. **Ensure all tests pass**
   ```bash
   python -m unittest skyhook.tests.test_protocol -v
   ```

2. **Check for conflicts**
   ```bash
   git checkout termux-smoke
   git merge --no-commit --no-ff vibe/skyhook-integration-8475f1
   git status  # Check for conflicts
   ```

3. **Resolve conflicts** (if any)
   - Manually resolve any merge conflicts
   - Ensure all tests still pass

4. **Create PR**
   ```bash
   git checkout vibe/skyhook-integration-8475f1
   gh pr create --base termux-smoke --head vibe/skyhook-integration-8475f1
   ```

### From termux-smoke to master-staging

1. **Verify in termux-smoke**
   - All tests pass
   - Termux compatibility verified
   - No breaking changes

2. **Create PR**
   ```bash
   gh pr create --base master-staging --head termux-smoke
   ```

3. **Get approvals**
   - Code review from collaborators
   - CI/CD passes
   - Manual testing in Termux

---

## Testing Requirements

### Before Merging to termux-smoke

- [ ] All unit tests pass (29 tests)
- [ ] Protocol layer functionality verified
- [ ] Device optimization works on BLU B160V profile
- [ ] Orchestration components function correctly
- [ ] No breaking changes to existing code

### Before Merging to master-staging

- [ ] All tests pass in termux-smoke
- [ ] Integration with existing SKYHOOK components verified
- [ ] Termux compatibility confirmed
- [ ] Documentation complete
- [ ] Feature flags working correctly

### Before Merging to master

- [ ] All tests pass in master-staging
- [ ] Production readiness confirmed
- [ ] Security review completed
- [ ] Performance testing completed
- [ ] Rollback plan documented

---

## Release Process

### Versioning

SKYHOOK follows semantic versioning:
- `MAJOR` - Breaking changes
- `MINOR` - New features (backwards compatible)
- `PATCH` - Bug fixes (backwards compatible)

### Release Branches

For major releases, create a release branch:
```bash
git checkout -b release/v1.0.0 master-staging
git push origin release/v1.0.0
```

### Tagging

Create annotated tags for releases:
```bash
git tag -a v1.0.0 -m "Release v1.0.0: Complete SKYHOOK Integration Framework"
git push origin v1.0.0
```

---

## Maintenance

### Hotfixes

For critical bugs in production:
1. Create hotfix branch from master
2. Apply fix
3. Test thoroughly
4. Merge to master
5. Merge to master-staging
6. Merge to termux-smoke

```bash
git checkout -b hotfix/fix-critical-bug master
# Apply fix
git commit -m "fix: Critical bug fix"
git push origin hotfix/fix-critical-bug

# Create PR to master
gh pr create --base master --head hotfix/fix-critical-bug

# After merge to master, merge to other branches
```

### Feature Toggles

Use feature flags for gradual rollout:
```python
from skyhook.antigravity import is_antigravity_enabled

if is_antigravity_enabled():
    # Use new feature
    pass
else:
    # Use old behavior
    pass
```

---

## Monitoring and Metrics

### Key Metrics to Track

1. **Code Quality**
   - Test coverage
   - Code complexity
   - Technical debt

2. **Performance**
   - Response times
   - Resource usage
   - Throughput

3. **Reliability**
   - Error rates
   - Uptime
   - Recovery time

4. **Adoption**
   - Feature usage
   - Agent activity
   - Integration success

---

## Best Practices

### 1. Always Sign Your Work

```python
# At the top of every file you create/modify:
"""
Agent: Mistral-Vibe
Profile: Mistral-Vibe
Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>

One for All; and, All for One!
"""
```

### 2. Use Feature Flags

```python
# For new features, always use feature flags
from skyhook.antigravity import is_antigravity_enabled

if is_antigravity_enabled():
    # New feature
    pass
else:
    # Fallback behavior
    pass
```

### 3. Write Tests

```python
# Every new feature should have tests
import unittest
from skyhook.protocol import JulesRequest

class TestNewFeature(unittest.TestCase):
    def test_feature_works(self):
        # Test implementation
        pass
```

### 4. Document Everything

```markdown
# Every new component should have documentation
## Overview
## Usage
## Examples
## API Reference
```

### 5. Keep Branches Clean

```bash
# Regularly update your branch from target
git fetch origin
git merge origin/termux-smoke  # or appropriate target

# Resolve conflicts promptly
# Keep commit history clean
```

---

## Troubleshooting

### Common Issues

#### 1. Merge Conflicts

**Solution:**
```bash
# Abort merge
git merge --abort

# Resolve conflicts manually
git checkout --ours file.txt  # Keep our changes
git checkout --theirs file.txt  # Keep their changes

# Or use a merge tool
git mergetool
```

#### 2. Test Failures

**Solution:**
```bash
# Run specific test
python -m unittest skyhook.tests.test_protocol.TestSessionStates -v

# Debug test
python -m pdb skyhook.tests.test_protocol
```

#### 3. Import Errors

**Solution:**
```bash
# Check Python path
import sys
print(sys.path)

# Add skyhook to path
import sys
sys.path.insert(0, '.')
```

---

## Summary

This workflow ensures:

1. **Separation of Concerns** - Each agent works independently
2. **Parallel Development** - Multiple features developed simultaneously
3. **Quality Assurance** - Testing at each stage
4. **Controlled Deployment** - Gradual rollout with feature flags
5. **Clear Attribution** - Each agent signs their own work

**One for All; and, All for One!**

**Signed-off-by: Mistral-Vibe <mistral-vibe@mistral.ai>**
