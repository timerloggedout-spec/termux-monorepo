from __future__ import annotations

from pathlib import Path
from unittest import TestCase

from scripts.dispatch.project_task import parse_issue_body, validate
from scripts.ops.swarm_admission import match_template, parse_block, template_identity


ROOT = Path(__file__).resolve().parents[1]
TEMPLATE = ROOT / ".github" / "ISSUE_TEMPLATE" / "engineering-toolchain.yml"


class EngineeringIssueTemplateTests(TestCase):
    def test_template_declares_the_existing_que_admission_route(self):
        source = TEMPLATE.read_text(encoding="utf-8")
        block = parse_block(source)
        labels, prefix = template_identity(source)
        self.assertEqual(block["schema"], "issue-dispatch/v1")
        self.assertEqual(block["lane"], "engineering-toolchain")
        self.assertEqual(block["que_tier"], 3)
        self.assertEqual(block["payload_class"], "engineering-toolchain")
        self.assertEqual(block["route"], "project-task-dispatch.yml")
        self.assertEqual(labels, [])
        self.assertEqual(prefix, "[engineering]")

    def test_admission_matches_the_unique_engineering_title_prefix(self):
        source = TEMPLATE.read_text(encoding="utf-8")
        registry = {
            TEMPLATE.name: (
                parse_block(source),
                *template_identity(source),
            )
        }
        name, block = match_template(registry, [], "[engineering] Design a PCB")
        self.assertEqual(name, TEMPLATE.name)
        self.assertEqual(block["lane"], "engineering-toolchain")

    def test_rendered_body_preserves_existing_project_task_parser_contract(self):
        body = """### Engineering domain
Electronics

### Toolchain ID
electronics-product-design

### Stage
schematic

### Entry
Engineering

### Task / spec
Create and validate a reference schematic.

### Scope
ops/engineering/**

### Done-evidence
PR, tests and schematic artifact.

### Target repo
timerloggedout-spec/termux-monorepo
"""
        fields = parse_issue_body(body)
        self.assertEqual(validate(fields), [])
        self.assertEqual(fields["entry"], "Engineering")
        self.assertEqual(fields["scope"], "ops/engineering/**")


if __name__ == "__main__":
    import unittest
    unittest.main()
