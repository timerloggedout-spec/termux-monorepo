# GitHub Projects Configuration

This file defines the project management structure for the termux-monorepo, including Projects, Milestones, and their relationships.

## Project Board Structure

### Active Projects

#### 1. Core Infrastructure (P0)
- **Description**: Foundational systems including ArchWiz, deepcli, and termux-multi-agent
- **Status**: Active
- **Milestones**: 
  - [M1: ArchWiz Stabilization](#milestone-m1-archwiz-stabilization)
  - [M2: DeepCLI Enhancement](#milestone-m2-deepcli-enhancement)
  - [M3: Multi-Agent Orchestration](#milestone-m3-multi-agent-orchestration)
- **Labels**: `core`, `infrastructure`, `P0`
- **Components**: `archwiz/`, `deepcli/`, `termux-multi-agent/`

#### 2. Conversation Synthesis (P1)
- **Description**: CLI synthegration, Chronos, and conversation management
- **Status**: Active
- **Milestones**:
  - [M4: Conversation Branching](#milestone-m4-conversation-branching)
  - [M5: Chronos Integration](#milestone-m5-chronos-integration)
- **Labels**: `synthegration`, `conversation`, `P1`
- **Components**: `cli-synthegration/`, `harmonizer-prod_cli/`

#### 3. Harmony & Multi-AI (P1)
- **Description**: Multi-model integration and harmony hub
- **Status**: Active
- **Milestones**:
  - [M6: Multi-Model CLI](#milestone-m6-multi-model-cli)
  - [M7: Harmony Hub Integration](#milestone-m7-harmony-hub-integration)
- **Labels**: `multi-ai`, `harmony`, `P1`
- **Components**: `multi-ai-cli/`, `harmony_hub/`

#### 4. Reference Templates (P2)
- **Description**: refTemplates restoration and organization
- **Status**: Active
- **Milestones**:
  - [M8: refTemplates Restoration](#milestone-m8-reftemplates-restoration)
  - [M9: Category Organization](#milestone-m9-category-organization)
- **Labels**: `reftemplates`, `documentation`, `P2`
- **Components**: `refTemplates/`

#### 5. Swarm & Commingle (P3)
- **Description**: Swarm ecosystem integration
- **Status**: Maintenance
- **Milestones**:
  - [M10: Commingle Swarm Integration](#milestone-m10-commingle-swarm-integration)
- **Labels**: `swarm`, `commingle`, `P3`
- **Components**: `commingle-swarm/`

#### 6. Projects & Exchanges (P2)
- **Description**: External projects and exchange integrations
- **Status**: Active
- **Milestones**:
  - [M11: Project Integration](#milestone-m11-project-integration)
  - [M12: Exchange API Updates](#milestone-m12-exchange-api-updates)
- **Labels**: `projects`, `exchanges`, `P2`
- **Components**: `_1-Projects/`, `exchanges/`

#### 7. Documentation & Navigation (P1)
- **Description**: Documentation, wiki, and navigation improvements
- **Status**: Active
- **Milestones**:
  - [M13: Documentation Pipeline](#milestone-m13-documentation-pipeline)
  - [M14: Navigation SSOT](#milestone-m14-navigation-ssot)
- **Labels**: `documentation`, `wiki`, `P1`
- **Components**: `wiki/`, `docs/`

#### 8. Security & Hygiene (P0)
- **Description**: Security improvements and repository hygiene
- **Status**: Active
- **Milestones**:
  - [M15: Session Store Hygiene](#milestone-m15-session-store-hygiene)
  - [M16: Security Remediation](#milestone-m16-security-remediation)
- **Labels**: `security`, `hygiene`, `P0`
- **Components**: `.github/workflows/`

---

## Milestones

### Milestone M1: ArchWiz Stabilization
- **Description**: Stabilize and enhance ArchWiz tooling
- **Due**: 2026-09-01
- **Priority**: P0
- **Status**: In Progress
- **Issues**:
  - Fix silent `except: pass` in dispatch pipeline
  - Implement config.py consumers across all tools
  - Archive legacy poller/listener components
  - Replace broken Termux absolute symlinks
- **Related PRs**: #1 (critical-proposal), mistral/fixes-config-security
- **Success Criteria**: All ArchWiz tools pass Sentinel gates

### Milestone M2: DeepCLI Enhancement
- **Description**: Enhance DeepCLI functionality and reliability
- **Due**: 2026-09-15
- **Priority**: P0
- **Status**: Planned
- **Issues**:
  - Add dispatch logging (no silent failures)
  - Fix send_message vs stream_completion payload divergence
  - Remove hardcoded session UUID fallback
  - Improve error handling and reporting
- **Related Components**: `deepcli/`, `deepcli-tui/`
- **Success Criteria**: All DeepCLI operations have proper logging and error handling

### Milestone M3: Multi-Agent Orchestration
- **Description**: Enhance termux-multi-agent capabilities
- **Due**: 2026-09-30
- **Priority**: P0
- **Status**: Planned
- **Issues**:
  - Improve agent provisioning and management
  - Enhance Cedar MCP server integration
  - Add better dashboard and status reporting
  - Implement run history tracking
- **Related Components**: `termux-multi-agent/`
- **Success Criteria**: Multi-agent system passes termux-smoke tests

### Milestone M4: Conversation Branching
- **Description**: Implement robust conversation branching and management
- **Due**: 2026-10-01
- **Priority**: P1
- **Status**: Planned
- **Issues**:
  - Enhance branch_manager.py functionality
  - Implement conv_branching.py improvements
  - Add conversation export and import capabilities
  - Improve Chronos integration
- **Related Components**: `cli-synthegration/`
- **Success Criteria**: Full conversation lifecycle management

### Milestone M5: Chronos Integration
- **Description**: Complete Chronos time-loop and versioning integration
- **Due**: 2026-10-15
- **Priority**: P1
- **Status**: Planned
- **Issues**:
  - Implement accelerator.py enhancements
  - Complete versioner.py integration
  - Add time-loop visualization
  - Implement success-only branching
- **Related Components**: `cli-synthegration/Chronos/`
- **Success Criteria**: Chronos pipeline fully integrated and tested

### Milestone M6: Multi-Model CLI
- **Description**: Enhance multi-AI model support
- **Due**: 2026-11-01
- **Priority**: P1
- **Status**: Planned
- **Issues**:
  - Add support for additional LLM providers
  - Implement model selection and switching
  - Add account management for multiple providers
  - Improve token management
- **Related Components**: `multi-ai-cli/`
- **Success Criteria**: Support for 3+ LLM providers with proper account management

### Milestone M7: Harmony Hub Integration
- **Description**: Complete Harmony Hub integration
- **Due**: 2026-11-15
- **Priority**: P1
- **Status**: Planned
- **Issues**:
  - Implement harmony_hub workspace integration
  - Add utility_belt tools to main workflow
  - Enhance token_provider_v2.py
  - Implement session management
- **Related Components**: `harmony_hub/`
- **Success Criteria**: Harmony Hub tools integrated into main workflow

### Milestone M8: refTemplates Restoration
- **Description**: Restore and organize refTemplates
- **Due**: 2026-08-15
- **Priority**: P2
- **Status**: In Progress
- **Issues**:
  - Merge recreate/refTemplates-skeleton to master
  - Add 15_Reverse_Engineering category
  - Nest Haven and Interpreted-Context-Methoddology_fork
  - Update README with refTemplates status
- **Related Components**: `refTemplates/`
- **Success Criteria**: All refTemplates categories restored as metadata-only

### Milestone M9: Category Organization
- **Description**: Organize and categorize all reference materials
- **Due**: 2026-09-01
- **Priority**: P2
- **Status**: Planned
- **Issues**:
  - Complete category 01-15 organization
  - Add metadata for all entries
  - Implement sparse checkout patterns
  - Update project mapping
- **Related Components**: `refTemplates/`, `workspace/llm_map/`
- **Success Criteria**: All refTemplates properly categorized and documented

### Milestone M10: Commingle Swarm Integration
- **Description**: Integrate commingle-swarm as template/scavenge resource
- **Due**: 2026-12-01
- **Priority**: P3
- **Status**: Planned
- **Issues**:
  - Document commingle-swarm usage patterns
  - Add selective integration points
  - Implement resource limits for Termux
  - Add cleanup and maintenance scripts
- **Related Components**: `commingle-swarm/`
- **Success Criteria**: Commingle-swarm properly documented and maintained

### Milestone M11: Project Integration
- **Description**: Integrate external projects into monorepo workflow
- **Due**: 2026-10-01
- **Priority**: P2
- **Status**: Planned
- **Issues**:
  - Update _1-Projects submodules
  - Add project discovery and indexing
  - Implement project health monitoring
  - Add project documentation
- **Related Components**: `_1-Projects/`
- **Success Criteria**: All projects indexed and discoverable

### Milestone M12: Exchange API Updates
- **Description**: Update exchange API integrations
- **Due**: 2026-11-01
- **Priority**: P2
- **Status**: Planned
- **Issues**:
  - Update yobitrageswap API integrations
  - Add new exchange APIs
  - Implement API health monitoring
  - Add error handling and retries
- **Related Components**: `_1-Projects/a/yobitrageswap/`, `exchanges/`
- **Success Criteria**: All exchange APIs functional and monitored

### Milestone M13: Documentation Pipeline
- **Description**: Complete documentation generation pipeline
- **Due**: 2026-09-15
- **Priority**: P1
- **Status**: Planned
- **Issues**:
  - Implement session_digest.py enhancements
  - Complete structural_scanner.py
  - Add export_status.py improvements
  - Implement pointer_index.py updates
- **Related Components**: `archwiz/` documentation tools
- **Success Criteria**: All documentation auto-generated and up-to-date

### Milestone M14: Navigation SSOT
- **Description**: Establish Single Source of Truth for navigation
- **Due**: 2026-08-30
- **Priority**: P1
- **Status**: In Progress
- **Issues**:
  - Update root README with navigation ladder
  - Fix REFERENCE_HUB absolute path links
  - Implement config-rooted entrypoints
  - Archive legacy Entry + HTML as secondary
- **Related Components**: `README.md`, `wiki/Navigation.md`, `archwiz/REFERENCE_HUB.md`
- **Success Criteria**: Clear navigation hierarchy established and documented

### Milestone M15: Session Store Hygiene
- **Description**: Remove session artifacts from Git tracking
- **Due**: 2026-08-10
- **Priority**: P0
- **Status**: In Progress
- **Issues**:
  - Fix pre-commit hook for session store scanning
  - Document credential rotation procedures
  - Implement history rewrite procedures
  - Add .gitignore patterns for session stores
- **Related PRs**: #3 (agent/repository-hygiene)
- **Success Criteria**: No session stores tracked in Git

### Milestone M16: Security Remediation
- **Description**: Address security vulnerabilities and implement best practices
- **Due**: 2026-09-01
- **Priority**: P0
- **Status**: Planned
- **Issues**:
  - Implement SECURITY-REMEDIATION.md procedures
  - Add security scanning to CI/CD
  - Implement credential management
  - Add security documentation
- **Related Components**: `.github/workflows/`, `docs/SECURITY-REMEDIATION.md`
- **Success Criteria**: Security gates pass for all PRs

---

## Label Definitions

### Priority Labels
- `P0`: Critical - Must be addressed immediately
- `P1`: High - Important features and improvements
- `P2`: Medium - Nice-to-have enhancements
- `P3`: Low - Future considerations

### Type Labels
- `bug`: Bug fixes
- `enhancement`: Feature enhancements
- `documentation`: Documentation improvements
- `security`: Security-related issues
- `maintenance`: Repository maintenance
- `refactor`: Code refactoring
- `performance`: Performance improvements

### Component Labels
- `archwiz`: ArchWiz-related
- `deepcli`: DeepCLI-related
- `synthegration`: CLI synthegration-related
- `multi-agent`: Multi-agent orchestration
- `harmony`: Harmony hub-related
- `reftemplates`: Reference templates
- `swarm`: Swarm/commingle-related
- `projects`: External projects
- `exchanges`: Exchange APIs

### Status Labels
- `good first issue`: Suitable for new contributors
- `help wanted`: Needs community assistance
- `needs review`: Ready for review
- `needs design`: Requires design discussion
- `blocked`: Blocked by dependencies
- `duplicate`: Duplicate issue
- `wontfix`: Will not be fixed

---

## Workflow Integration

### GitHub Projects Board
The main project board tracks progress across all milestones and projects. Each issue and PR should be:
1. Assigned to the appropriate Project
2. Labeled with priority and type
3. Linked to relevant milestones
4. Updated with progress status

### CI/CD Integration
- All PRs must pass repo-gate and termux-smoke
- Security-related changes require additional security gates
- Documentation updates should trigger wiki publishing

### Automation
- Use `scripts/proposals/` for proposal lifecycle management
- Use `archwiz/` tools for code analysis and validation
- Use `.github/workflows/` for automated processes

---

## Maintenance

### Regular Tasks
- Update registry.yaml with new proposals
- Review and prioritize open issues
- Update milestone progress
- Clean up completed milestones
- Archive old projects and issues

### Review Process
1. All changes must be reviewed by at least one other contributor
2. P0 changes require Operator approval
3. Security changes require security team review
4. Documentation changes can be merged with single approval

---

## Quick Reference

| Action | Command/Location |
|--------|------------------|
| View Projects | GitHub Projects tab |
| View Milestones | GitHub Milestones page |
| Create Issue | Use issue templates in `.github/ISSUE_TEMPLATE/` |
| Create PR | Use PR template in `.github/PULL_REQUEST_TEMPLATE.md` |
| Run Tests | `python3 scripts/ci/repo_gate.py` |
| Run Termux Smoke | `python3 scripts/ci/termux_smoke.py` |
| Update Documentation | `python3 archwiz/session_digest.py` |

---

*Last updated: 2026-08-06*
*Maintainer: @timerloggedout-spec*
