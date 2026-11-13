---
id: agent-readability-surface-contract
title: "Agent Readability Source, Deployment, and Authoring Contract"
author: ChatGPT
posted_at: 2026-11-13
source: operator-directive
status: accepted
priority: P1
reviewers:
  - id: timerloggedout-spec
    role: operator-authorizer
    status: accepted
related_issues: []
related_prs:
  - 5336
related_branches:
  - feat/agent-readability-do-mandate-v2
gates_required: [repo-gate, termux-smoke]
---

# MANIFEST — agent-readability-surface-contract

## Purpose

Publish agent-readable HTML and Markdown from canonical source files, preserve source-to-publication provenance, enforce the DO-statement authoring contract, and reserve public recognition for verified Agent Readability scores of 95 or higher.

## Operator authorization

The operator directly requested remediation, repository-wide DO statements, skill inclusion, the conditional score badge, and continued implementation on 2026-11-13. This authorization establishes the execution scope for the listed items.

## Ownership

- HTML and Markdown source surfaces: their owning project directories.
- GitHub Pages publication: `.github/workflows/tribute-dashboard-deploy.yml`.
- Agent readability source contract: `scripts/ci/verify_agent_readability_surfaces.py`.
- Repository authoring style: `docs/ops/DO-STATEMENT-MANDATE.md`.
- Public score badge: the website repository, driven by a verified scan receipt.

## Boundaries

Static GitHub Pages publishes sibling Markdown files and HTML alternate links. Runtime content negotiation and custom response headers require an edge or server capability. Internal experimental encodings remain separate from public crawler-facing content.

## Review and closeout

Record the source SHA, publication SHA, workflow run, live URLs, Agent Ready scan ID, score, and unresolved checks. Promotion follows the repository dual gates and verified publication outcome.


## Related website changes

- Website PR #48: conditional 95+ badge renderer, cache refresh, and source validator.
- Website PR #49: primary WebPage breadcrumb, static text expansion, and accessible badge label; awaiting CI and publication.
