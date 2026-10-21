#!/usr/bin/env python3
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
PATH = ROOT / '.github/workflows/pr-evidence-evaluation.yml'

def test_pr_evidence_evaluation_is_read_only():
    text = PATH.read_text(encoding='utf-8')
    assert 'issues: write' not in text
    assert 'pull-requests: write' not in text
    assert 'contents: write' not in text
    assert 'github.rest.issues.createComment' not in text
    assert 'gh pr create' not in text
    assert 'pulls.create' not in text

if __name__ == '__main__':
    test_pr_evidence_evaluation_is_read_only()
    print('PR evidence evaluation side-effect policy: PASS')
