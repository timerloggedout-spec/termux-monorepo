---
id: ml-pipeline-keep
title: "ML pipeline keep-alive DAG (extract-only vs #432/#601)"
author: grok
posted_at: 2026-09-20
status: executing
priority: P1
---

# MANIFEST — ml-pipeline-keep

Extract-only keep-alive for Issue #175 ML lanes.
Do not wholesale-merge #432 or #601.

DAG: `ml/pipelines/`
Skill: `.agents/skills/ml-pipeline-ops/SKILL.md`
Gates: repo-gate + termux-smoke
