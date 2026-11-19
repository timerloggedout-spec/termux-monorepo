Monitor a long-running process with increasing check intervals.

Ask me: What command should I run to check status?

Then:
1. Run the status command
2. Report: timestamp, status summary (one line)
3. Sleep with increasing intervals: 30s, 60s, 120s, 240s, then cap at 300s
4. Repeat until complete or failed

On completion: summarize the final result.
On failure: report the error and suggest next steps.

Keep output minimal — one status line per check. Do not stream full logs.

For GitHub CI specifically: use `gh run view <id> | head -20` instead of `gh run watch` (the latter wastes tokens with continuous output).
