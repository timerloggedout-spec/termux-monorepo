Verify the work from this session.

First: check if any files were created or modified during this session. If none were, exit silently — do not produce an empty report.

If files were changed, for each one apply the most concrete verification available:
- **Code files:** Execute or compile. Report pass/fail.
- **Scripts:** Run with test inputs if possible. Check exit code and output format.
- **Config/JSON:** Validate syntax (json parse, yaml lint, etc.)
- **File operations:** Confirm files exist at expected paths with expected content.
- **Text/analysis:** State "not programmatically testable" — do not fake verification.

Present results:

| File | Verification | Result |
|---|---|---|
| path/to/file | How you tested it | Pass / Fail / Untestable |

If any failures: fix them, then re-verify the fixed files.
